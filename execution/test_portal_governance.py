"""
MAK Collaboration Portal: role governance and full user flow test.

Serves portal/ on localhost, drives it with headless Chromium as Idrees and as MAK,
and verifies every write against the live Supabase project through PostgREST.

Run:
  /home/idrees/job_agent/.venv/bin/python3 execution/test_portal_governance.py

Safety:
  * Requests to Supabase Auth (/auth/v1/) are aborted, so portal passwords never leave localhost.
  * Native confirm() and prompt() are auto cancelled, exactly like embedded browsers do, so any
    flow that still depends on them fails here.
  * Every row this test creates carries a run tag and is deleted at the end.
  * MAK availability is toggled twice, so it ends in its original state.
"""

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
from playwright.sync_api import sync_playwright, expect

PORTAL_DIR = Path(__file__).resolve().parent.parent / "portal"

SUPABASE_URL = "https://uamrtiorazuuutkjxdov.supabase.co"
# Publishable key: already shipped to every browser in portal/js/supabase-client.js
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_IL_Mg9UB5IhpjmWZMtYJNg_wjHgUktP")
REST = f"{SUPABASE_URL}/rest/v1"
REST_HEADERS = {"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}"}

IDREES = (os.environ.get("PORTAL_IDREES_EMAIL", "idrees@kabani.ai"), os.environ.get("PORTAL_IDREES_PASSWORD", "Idrees2026!"))
MAK = (os.environ.get("PORTAL_MAK_EMAIL", "mak@kabani.ai"), os.environ.get("PORTAL_MAK_PASSWORD", "Mak2026!"))

RUN_TAG = f"GOVTEST{int(time.time())}"
TIMEOUT_MS = 15000
SETTLE = 2  # seconds for realtime echoes to land before asserting nothing reappeared

results = []
native_dialogs = []


def check(name, fn):
    try:
        fn()
        results.append((True, name, ""))
        print(f"  PASS  {name}")
    except Exception as exc:
        msg = str(exc).strip().splitlines()[0] if str(exc).strip() else type(exc).__name__
        results.append((False, name, msg))
        print(f"  FAIL  {name}\n        {msg}")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# ── PostgREST helpers ────────────────────────────────────────────────────────

def rest_get(path):
    r = requests.get(f"{REST}/{path}", headers=REST_HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def rows(table, column, value, select="*"):
    return rest_get(f"{table}?select={select}&{column}=eq.{quote(value)}")


def wait_until(predicate, what, timeout=20):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = predicate()
        if last:
            return last
        time.sleep(1)
    raise AssertionError(f"timed out waiting for {what}")


def wait_for_row(table, column, value, timeout=20):
    return wait_until(lambda: (rows(table, column, value) or [None])[0], f"{table}.{column} = '{value}'", timeout)


def wait_for_field(table, column, value, field, expected, timeout=20):
    def ok():
        found = rows(table, column, value)
        return found and found[0].get(field) == expected
    wait_until(ok, f"{table} '{value}' {field} == {expected!r}", timeout)


def wait_for_gone(table, column, value, timeout=20):
    wait_until(lambda: not rows(table, column, value, "id"), f"{table} '{value}' to be deleted", timeout)


def mak_status():
    found = rest_get("user_availability?select=status&user_id=eq.mak")
    return found[0]["status"] if found else None


# ── Browser helpers ──────────────────────────────────────────────────────────

def new_context(browser):
    ctx = browser.new_context()
    ctx.route("**/auth/v1/**", lambda route: route.abort())
    return ctx


def new_page(ctx):
    page = ctx.new_page()

    def on_dialog(dialog):
        native_dialogs.append(f"{dialog.type}: {dialog.message}")
        dialog.dismiss()
    page.on("dialog", on_dialog)
    return page


def login(page, base, creds):
    page.goto(f"{base}/auth/login.html")
    page.fill("#email", creds[0])
    page.fill("#password", creds[1])
    page.click("button[type=submit]")


def assert_path(page, suffix):
    page.wait_for_url(f"**/{suffix}", timeout=TIMEOUT_MS)
    page.wait_for_load_state("domcontentloaded")


def open_page(page, base, path, ready_selector):
    page.goto(f"{base}/{path}")
    page.wait_for_selector(ready_selector, timeout=TIMEOUT_MS)
    time.sleep(1.5)  # initial Supabase fetch and realtime subscribe


def dialog_answer(page, confirm=True):
    dlg = page.locator(".portal-dialog")
    expect(dlg).to_be_visible(timeout=TIMEOUT_MS)
    dlg.locator(".portal-dialog-confirm" if confirm else ".portal-dialog-cancel").click()
    expect(dlg).to_have_count(0)


def expand(card, header_selector):
    if "expanded" not in (card.get_attribute("class") or ""):
        card.locator(header_selector).first.click()


def assert_no_toast(page):
    toasts = page.locator(".portal-toast")
    assert toasts.count() == 0, f"error toast shown: {toasts.first.inner_text()}"


def delete_via_ui(page, card, button_selector, table, column, value):
    """Cancel once (nothing happens), then confirm; the row must leave the DB and stay out of the DOM."""
    card.locator(button_selector).click()
    dialog_answer(page, confirm=False)
    time.sleep(1)
    assert card.count() == 1, "item vanished after Cancel"
    assert rows(table, column, value, "id"), "row deleted after Cancel"
    card.locator(button_selector).click()
    dialog_answer(page, confirm=True)
    wait_for_gone(table, column, value)
    time.sleep(SETTLE)
    assert card.count() == 0, "deleted item reappeared in the page"
    assert_no_toast(page)


# ── Flows ────────────────────────────────────────────────────────────────────

def post_project(page, base, page_file, button_text, name, role, expected_status):
    open_page(page, base, page_file, "#btn-post-project")
    btn = page.locator("#btn-post-project")
    expect(btn).to_be_visible(timeout=TIMEOUT_MS)
    expect(btn).to_have_text(button_text)
    btn.click()
    expect(page.locator("#modal-post-project")).to_be_visible()
    page.fill("#proj-name", name)
    page.fill("#proj-brief", f"Test brief by {role}")
    page.fill("#proj-desc", "Created by test_portal_governance.py and deleted at the end of the run.")
    page.fill("#proj-reqs", "Playwright, PostgREST")
    page.select_option("#proj-priority", "low")
    page.click("#form-post-project button[type=submit]")
    expect(page.locator("#modal-post-project")).to_be_hidden()
    expect(page.locator("#projects-grid")).to_contain_text(name, timeout=TIMEOUT_MS)
    row = wait_for_row("projects", "name", name)
    assert row["status"] == expected_status, f"status is '{row['status']}', expected '{expected_status}'"
    assert row["posted_by"] == role, f"posted_by is '{row['posted_by']}', expected '{role}'"
    time.sleep(SETTLE)
    assert page.locator(".project-card", has_text=name).count() == 1, "project card missing or duplicated"


def add_task(page, base, todos_file, title, assigned_to, created_by):
    open_page(page, base, todos_file, "#btn-add-task")
    page.click("#btn-add-task")
    page.fill("#task-title", title)
    page.fill("#task-desc", "Task created by the governance test")
    page.select_option("#task-urgency", "high")
    page.click("#add-task-form button[type=submit]")
    row = wait_for_row("todos", "title", title)
    assert row["assigned_to"] == assigned_to, f"assigned_to is {row['assigned_to']}"
    assert row["created_by"] == created_by, f"created_by is {row['created_by']}"
    time.sleep(SETTLE)
    count = page.locator(".task-row", has_text=title).count()
    assert count == 1, f"task rendered {count} times"
    assert len(rows("todos", "title", title, "id")) == 1, "task saved more than once"
    assert_no_toast(page)


def task_actions(page, title):
    row = page.locator(".task-row", has_text=title)
    expand(row, ".task-row-main")
    row.locator(".notes-ta").fill("note from test")
    row.locator(".notes-ta").press("Tab")
    wait_for_field("todos", "title", title, "notes", "note from test")
    time.sleep(1)

    expand(row, ".task-row-main")
    row.locator('.status-btn[data-status="in_progress"]').click()
    wait_for_field("todos", "title", title, "status", "in_progress")
    time.sleep(SETTLE)
    expect(row.locator(".task-row-title")).to_have_text(title)
    expect(row.locator(".status-chip")).to_have_text("In Progress")

    expand(row, ".task-row-main")
    row.locator(".btn-pin").click()
    wait_for_field("todos", "title", title, "pinned", True)
    time.sleep(SETTLE)
    expect(row.locator(".pin-tag")).to_be_visible()
    assert page.locator(".task-row", has_text=title).count() == 1, "task duplicated after updates"
    assert_no_toast(page)


def run_idrees(browser, base, names):
    print("\n[Idrees: master admin]")
    ctx = new_context(browser)
    page = new_page(ctx)

    check("login lands on index.html", lambda: (login(page, base, IDREES), assert_path(page, "index.html")))

    def sees_switch_on_index():
        btn = page.locator("#btn-switch-portal")
        expect(btn).to_be_visible(timeout=TIMEOUT_MS)
        expect(btn).to_contain_text("Switch to MAK Portal")
    check("index.html shows 'Switch to MAK Portal'", sees_switch_on_index)

    check("New Projects: '+ Post Project' creates a project (status new)",
          lambda: post_project(page, base, "projects-new.html", "+ Post Project", names["idrees_new"], "idrees", "new"))

    def accept_project():
        card = page.locator(".project-card", has_text=names["idrees_new"])
        expand(card, ".project-card-header")
        card.locator(".btn-accept-project").click()
        wait_for_field("projects", "name", names["idrees_new"], "status", "accepted")
        todo = wait_for_row("todos", "title", f"Project: {names['idrees_new']}")
        assert todo["assigned_to"] == "idrees" and todo["related_project"], "auto task not linked"
        time.sleep(SETTLE)
        assert card.count() == 0, "accepted project still listed under New Projects"
        assert_no_toast(page)
    check("New Projects: 'Accept Project' moves it to ongoing and creates the linked Idrees task", accept_project)

    def accepted_shows_ongoing_and_deletes():
        open_page(page, base, "projects-ongoing.html", "#btn-post-project")
        card = page.locator(".project-card", has_text=names["idrees_new"])
        expect(card).to_have_count(1)
        delete_via_ui(page, card, ".btn-delete-project-quick", "projects", "name", names["idrees_new"])
    check("Ongoing Projects: accepted project listed; 🗑 delete (cancel, then confirm) removes it", accepted_shows_ongoing_and_deletes)

    check("Ongoing Projects: '+ Add Project' creates a project (status active)",
          lambda: post_project(page, base, "projects-ongoing.html", "+ Add Project", names["idrees_ongoing"], "idrees", "active"))

    def save_state():
        card = page.locator(".project-card", has_text=names["idrees_ongoing"])
        expand(card, ".project-card-header")
        card.locator('textarea[name="current_state"]').fill("Halfway there")
        card.locator('input[name="progress"]').fill("40")
        card.locator('button[type="submit"]').click()
        wait_for_field("projects", "name", names["idrees_ongoing"], "progress", 40)
        wait_for_field("projects", "name", names["idrees_ongoing"], "current_state", "Halfway there")
        time.sleep(SETTLE)
        expect(card.locator(".progress-label")).to_have_text("40%")
        assert_no_toast(page)
    check("Ongoing Projects: 'Save State' persists progress and current state", save_state)

    def delete_ongoing_body_button():
        card = page.locator(".project-card", has_text=names["idrees_ongoing"])
        expand(card, ".project-card-header")
        delete_via_ui(page, card, ".btn-delete-project", "projects", "name", names["idrees_ongoing"])
    check("Ongoing Projects: 'Delete Project' button removes it", delete_ongoing_body_button)

    check("Idrees Tasks: '+ Add Task' saves once to Supabase and renders once",
          lambda: add_task(page, base, "todos-idrees.html", names["idrees_task"], "idrees", "idrees"))
    check("Idrees Tasks: notes, status and pin all persist", lambda: task_actions(page, names["idrees_task"]))

    def delete_task():
        row = page.locator(".task-row", has_text=names["idrees_task"])
        delete_via_ui(page, row, ".btn-delete-quick", "todos", "title", names["idrees_task"])
    check("Idrees Tasks: 🗑 delete removes the task", delete_task)

    check("MAK Tasks: Idrees assigns a task to MAK",
          lambda: add_task(page, base, "todos-mak.html", names["task_for_mak"], "mak", "idrees"))

    def create_and_submit_proposal():
        open_page(page, base, "proposals.html", "#proposals-grid")
        btn = page.locator("#btn-new-proposal")
        expect(btn).to_be_visible(timeout=TIMEOUT_MS)
        btn.click()
        page.fill("#prop-title", names["proposal"])
        page.fill("#prop-hours", "3")
        page.fill("#prop-body", "Proposal created by the governance test")
        page.fill("#prop-benefits", "Faster, Cheaper")
        page.click("#form-new-proposal button[type=submit]")
        wait_for_field("proposals", "title", names["proposal"], "status", "draft")
        time.sleep(SETTLE)
        card = page.locator(".proposal-card", has_text=names["proposal"])
        assert card.count() == 1, "proposal card missing or duplicated"
        expand(card, ".proposal-card-header")
        card.get_by_role("button", name="Submit to MAK").click()
        wait_for_field("proposals", "title", names["proposal"], "status", "submitted")
        assert_no_toast(page)
    check("Proposals: create draft, then 'Submit to MAK'", create_and_submit_proposal)

    def inquiry_ask_and_delete():
        open_page(page, base, "index.html", "#form-ask-inquiry")
        question = names["inquiry"]
        page.fill("#input-new-inquiry", question)
        page.click("#form-ask-inquiry button[type=submit]")
        item = page.locator(".inq-row", has_text=question)
        expect(item).to_have_count(1)
        item.locator(".btn-delete-inquiry").click()
        dialog_answer(page, confirm=False)
        expect(item).to_have_count(1)
        item.locator(".btn-delete-inquiry").click()
        dialog_answer(page, confirm=True)
        expect(item).to_have_count(0)
    check("Home inquiries: ask a question, delete (cancel, then confirm)", inquiry_ask_and_delete)

    def hours_log_and_delete():
        open_page(page, base, "hours.html", "#btn-add-session")
        page.click("#btn-add-session")
        expect(page.locator(".portal-dialog")).to_be_visible()
        page.fill("#portal-dialog-focus", names["session"])
        page.fill("#portal-dialog-hours", "1.5")
        page.locator(".portal-dialog-confirm").click()
        entry = page.locator("#page-history-tbody tr", has_text=names["session"])
        expect(entry).to_have_count(1)
        expect(entry).to_contain_text("1.5h")
        entry.locator(".btn-delete-session").click()
        dialog_answer(page, confirm=True)
        expect(entry).to_have_count(0)
    check("Hours: '+ Log Session' and session Delete work", hours_log_and_delete)

    def switch_to_mak():
        open_page(page, base, "index.html", "#btn-switch-portal")
        page.locator("#btn-switch-portal").click()
        assert_path(page, "mak.html")
        assert page.evaluate("localStorage.getItem('portal_active_role')") == "mak"
    check("'Switch to MAK Portal' navigates to mak.html", switch_to_mak)

    def sees_return_on_mak():
        btn = page.locator("#btn-switch-portal")
        expect(btn).to_be_visible(timeout=TIMEOUT_MS)
        expect(btn).to_contain_text("Return to Idrees Portal")
        time.sleep(1)
        assert page.url.endswith("mak.html"), f"Idrees was bounced off mak.html to {page.url}"
    check("mak.html shows 'Return to Idrees Portal' and Idrees is not bounced", sees_return_on_mak)

    def preview_is_read_only():
        expect(page.locator(".mak-avail-pill")).to_be_visible(timeout=TIMEOUT_MS)
        assert page.locator("#btn-mak-availability").count() == 0, "Idrees preview can toggle MAK availability"
        assert page.locator('a[href="todos-idrees.html"]').count() == 0, "MAK view links to Idrees Tasks"
    check("MAK view preview: availability read only, no Idrees Tasks link", preview_is_read_only)

    def return_to_idrees():
        page.locator("#btn-switch-portal").click()
        assert_path(page, "index.html")
        page.wait_for_function("localStorage.getItem('portal_active_role') === 'idrees'", timeout=TIMEOUT_MS)
    check("'Return to Idrees Portal' navigates to index.html and restores the Idrees role", return_to_idrees)

    ctx.close()


def run_mak(browser, base, names):
    print("\n[MAK: partner]")
    ctx = new_context(browser)
    page = new_page(ctx)

    check("login lands on mak.html", lambda: (login(page, base, MAK), assert_path(page, "mak.html")))

    def no_switch_button():
        expect(page.locator(".hero-headline")).to_be_visible(timeout=TIMEOUT_MS)
        page.wait_for_function("document.readyState === 'complete'")
        time.sleep(1)
        assert page.locator("#btn-switch-portal").count() == 0, "switch button exists in MAK's DOM"
        assert page.get_by_text("Idrees Portal").count() == 0, "an 'Idrees Portal' control is rendered"
        assert page.locator('a[href="todos-idrees.html"]').count() == 0, "Idrees Tasks card is linked"
    check("mak.html has no switch button and no Idrees Tasks link", no_switch_button)

    for target in ("index.html", "todos-idrees.html", ""):
        label = target or "/ (root)"

        def blocked(target=target):
            page.goto(f"{base}/{target}")
            assert_path(page, "mak.html")
        check(f"direct navigation to {label} redirects to mak.html", blocked)

    check("New Projects: MAK posts a project (status new)",
          lambda: post_project(page, base, "projects-new.html", "+ Post Project", names["mak_new"], "mak", "new"))

    def mak_delete_new():
        card = page.locator(".project-card", has_text=names["mak_new"])
        delete_via_ui(page, card, ".btn-delete-project-quick", "projects", "name", names["mak_new"])
    check("New Projects: MAK 🗑 delete (cancel, then confirm) removes it", mak_delete_new)

    check("Ongoing Projects: MAK adds a project (status active)",
          lambda: post_project(page, base, "projects-ongoing.html", "+ Add Project", names["mak_ongoing"], "mak", "active"))

    def back_link_home():
        href = page.locator("a.back-arrow").get_attribute("href")
        assert href == "mak.html", f"back link points to {href}"
    check("back link on project pages points MAK to mak.html", back_link_home)

    def mak_delete_ongoing():
        card = page.locator(".project-card", has_text=names["mak_ongoing"])
        delete_via_ui(page, card, ".btn-delete-project-quick", "projects", "name", names["mak_ongoing"])
    check("Ongoing Projects: MAK 🗑 delete removes it", mak_delete_ongoing)

    def sees_assigned_task():
        open_page(page, base, "todos-mak.html", "#btn-add-task")
        row = page.locator(".task-row", has_text=names["task_for_mak"])
        expect(row).to_have_count(1, timeout=TIMEOUT_MS)
        expand(row, ".task-row-main")
        row.locator('.status-btn[data-status="done"]').click()
        wait_for_field("todos", "title", names["task_for_mak"], "status", "done")
        time.sleep(SETTLE)
        expect(row.locator(".task-row-title")).to_have_text(names["task_for_mak"])
        assert_no_toast(page)
    check("MAK Tasks: MAK sees the task Idrees assigned and marks it Done", sees_assigned_task)

    check("MAK Tasks: MAK adds his own task", lambda: add_task(page, base, "todos-mak.html", names["mak_task"], "mak", "mak"))

    def mak_deletes_tasks():
        for title in (names["mak_task"], names["task_for_mak"]):
            row = page.locator(".task-row", has_text=title)
            expand(row, ".task-row-main")
            delete_via_ui(page, row, ".btn-delete", "todos", "title", title)
    check("MAK Tasks: 'Delete' button removes tasks", mak_deletes_tasks)

    def mak_answers_proposal():
        open_page(page, base, "proposals.html", "#proposals-grid")
        assert page.locator("#btn-new-proposal").is_hidden(), "MAK sees 'New Proposal'"
        card = page.locator(".proposal-card", has_text=names["proposal"])
        expect(card).to_have_count(1, timeout=TIMEOUT_MS)
        expand(card, ".proposal-card-header")
        card.locator(".mak-resp").fill("Approved, go ahead")
        card.locator(".btn-accept-prop").click()
        wait_for_field("proposals", "title", names["proposal"], "status", "accepted")
        wait_for_field("proposals", "title", names["proposal"], "mak_response", "Approved, go ahead")
        assert_no_toast(page)
    check("Proposals: MAK sees Idrees' submitted proposal and accepts with a response", mak_answers_proposal)

    def mak_deletes_proposal():
        card = page.locator(".proposal-card", has_text=names["proposal"])
        delete_via_ui(page, card, ".btn-delete-proposal-quick", "proposals", "title", names["proposal"])
    check("Proposals: 🗑 delete removes the proposal", mak_deletes_proposal)

    def availability_round_trip():
        original = mak_status()
        assert original in ("available", "away"), f"unexpected starting status '{original}'"
        flipped = "away" if original == "available" else "available"
        open_page(page, base, "mak.html", "#btn-mak-availability")
        btn = page.locator("#btn-mak-availability")
        expect(btn).to_contain_text("Available" if original == "available" else "Away")
        btn.click()
        wait_until(lambda: mak_status() == flipped, f"availability '{flipped}'")
        page.locator("#btn-mak-availability").click()
        wait_until(lambda: mak_status() == original, f"availability back to '{original}'")
    check("availability toggle writes to Supabase both ways (state restored)", availability_round_trip)

    ctx.close()


def cleanup():
    removed = 0
    for table, column in (("todos", "title"), ("proposals", "title"), ("projects", "name")):
        r = requests.delete(f"{REST}/{table}?{column}=like.*{RUN_TAG}*",
                            headers={**REST_HEADERS, "Prefer": "return=representation"}, timeout=20)
        r.raise_for_status()
        removed += len(r.json())
    print(f"\nCleanup: removed {removed} leftover test rows tagged {RUN_TAG}")


def main():
    names = {key: f"[{RUN_TAG}] {label}" for key, label in {
        "idrees_new": "Idrees new project",
        "idrees_ongoing": "Idrees ongoing project",
        "idrees_task": "Idrees task",
        "task_for_mak": "Task for MAK",
        "proposal": "Proposal",
        "inquiry": "Inquiry",
        "session": "Session",
        "mak_new": "MAK new project",
        "mak_ongoing": "MAK ongoing project",
        "mak_task": "MAK task",
    }.items()}

    port = free_port()
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=PORTAL_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                requests.get(base, timeout=1)
                break
            except requests.ConnectionError:
                time.sleep(0.1)
        print(f"Serving {PORTAL_DIR} at {base} (run tag {RUN_TAG})")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                run_idrees(browser, base, names)
                run_mak(browser, base, names)
            finally:
                browser.close()
    finally:
        server.terminate()
        cleanup()

    check("no flow opened a native confirm() or prompt() dialog",
          lambda: (_ for _ in ()).throw(AssertionError("; ".join(native_dialogs))) if native_dialogs else None)

    failed = [r for r in results if not r[0]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
