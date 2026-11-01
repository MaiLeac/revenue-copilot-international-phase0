import asyncio
from pathlib import Path

from patchright.async_api import async_playwright
from plugins._browser.helpers.playwright import ensure_playwright_binary
from plugins._code_execution.helpers.shell_local import LocalInteractiveSession


async def main():
    test_file = Path("/a0/usr/workdir/codex-smoke-test.txt")
    test_file.write_text("agent-zero-file-ok\n", encoding="utf-8")
    print(f"FILE:{test_file.read_text(encoding='utf-8').strip()}")

    shell = LocalInteractiveSession(cwd="/a0/usr/workdir")
    await shell.connect()
    try:
        await shell.send_command("printf agent-zero-terminal-ok")
        output, _ = await shell.read_output(timeout=2)
        print(f"TERMINAL:{'agent-zero-terminal-ok' in output}")
    finally:
        await shell.close()

    executable = str(ensure_playwright_binary())
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=executable,
            headless=True,
            args=["--no-sandbox"],
        )
        page = await browser.new_page()
        response = await page.goto("https://example.com", wait_until="domcontentloaded")
        print(f"BROWSER:{response.status if response else 'none'}:{await page.title()}")
        await browser.close()


asyncio.run(main())
