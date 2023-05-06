# Copyright (c) Microsoft Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from typing import Any, Callable, Dict, Optional, List

from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Error,
    Page,
    Playwright,
    sync_playwright,
)
import functools


def _is_debugger_attached() -> bool:
    pydevd = sys.modules.get("pydevd")
    if not pydevd or not hasattr(pydevd, "get_global_debugger"):
        return False
    debugger = pydevd.get_global_debugger()
    if not debugger or not hasattr(debugger, "is_attached"):
        return False
    return debugger.is_attached()


after_all_tasks_run: Any = None
after_task_run: Any = None


def _session_cache(func):
    cache = []

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        if cache:
            return cache[0]

        ret = func(*args, **kwargs)

        cache.append(ret)

        def call_after_tasks_run(*args, **kwargs):
            cache.clear()
            after_all_tasks_run.unregister(call_after_tasks_run)

        after_all_tasks_run.register(call_after_tasks_run)

    return new_func


def _task_cache(func):
    cache = []

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        if cache:
            return cache[0]

        ret = func(*args, **kwargs)

        cache.append(ret)

        def call_after_task_run(*args, **kwargs):
            cache.clear()
            after_task_run.unregister(call_after_task_run)

        after_task_run.register(call_after_task_run)

    return new_func


class _PlayWrightBrowserContext:
    def __init__(
        self,
        browser_engine,
        headless: Optional[bool] = None,
        slowmo: int = 0,
        tracing: str = "off",
        video: str = "off",
        screenshot: str = "off",
    ):
        """
        Args:
            browser_engine:
                help="Browser engine which should be used",
                choices=["chromium", "firefox", "webkit"],

            headless:
                Run headless or not.

            slowmo:
                Run interactions in slow motion.

            tracing:
                default="off",
                choices=["on", "off", "retain-on-failure"],
                help="Whether to record a trace for each task.",

            video:
                default="off",
                choices=["on", "off", "retain-on-failure"],
                help="Whether to record video for each task.",

            screenshot:
                default="off",
                choices=["on", "off", "only-on-failure"],
                help="Whether to automatically capture a screenshot after each task.",
        """
        self.browser_engine = browser_engine

        if headless is None:
            headless = _is_debugger_attached()

        self.headless = headless
        self.slowmo = slowmo
        self.tracing = tracing
        self.video = video
        self.screenshot = screenshot

    @property
    @_session_cache
    def browser_context_args(
        self,
    ) -> Dict:
        pytestconfig: Any
        playwright: Playwright
        device: Optional[str]
        base_url: Optional[str]
        context_args = {}
        if device:
            context_args.update(playwright.devices[device])
        if base_url:
            context_args["base_url"] = base_url

        video_option = pytestconfig.getoption("--video")
        capture_video = video_option in ["on", "retain-on-failure"]
        if capture_video:
            context_args["record_video_dir"] = artifacts_folder.name

        return context_args

    @property
    @_session_cache
    def playwright(self) -> Playwright:
        pw = sync_playwright().start()

        # Need to stop when tasks finish running.
        def _auto_close():
            pw.stop()
            after_all_tasks_run.unregister(_auto_close)

        after_all_tasks_run.register(_auto_close)
        return pw

    @property
    @_session_cache
    def _browser_type(self) -> BrowserType:
        playwright = self.playwright

        return getattr(playwright, self.browser_engine)

    @property
    @_session_cache
    def _launch_browser(self) -> Callable[..., Browser]:
        browser_type_launch_args: Dict = {
            "headless": self.headless,
            "slow_mo": self.slowmo,
        }
        browser_type: BrowserType = self._browser_type()

        def launch(**kwargs: Dict) -> Browser:
            launch_options = {**browser_type_launch_args, **kwargs}
            browser = browser_type.launch(**launch_options)
            return browser

        return launch

    @property
    @_session_cache
    def browser(
        self,
    ) -> Browser:
        # Note: one per session (must be tear-down).
        browser = self._launch_browser()

        def _auto_close():
            browser.close()
            after_all_tasks_run.unregister(_auto_close)

        after_all_tasks_run.register(_auto_close)
        return browser

    @property
    @_task_cache
    def context(self) -> BrowserContext:
        browser: Browser = self.browser
        browser_context_args: Dict = self.browser_context_args
        pytestconfig: Any

        pages: List[Page] = []
        context = browser.new_context(**browser_context_args)
        context.on("page", lambda page: pages.append(page))

        tracing_option = self.tracing
        capture_trace = tracing_option in ["on", "retain-on-failure"]
        if capture_trace:
            context.tracing.start(
                title=slugify(request.node.nodeid),
                screenshots=True,
                snapshots=True,
                sources=True,
            )

        yield context

        # If requst.node is missing rep_call, then some error happened during execution
        # that prevented teardown, but should still be counted as a failure
        failed = (
            request.node.rep_call.failed if hasattr(request.node, "rep_call") else True
        )

        if capture_trace:
            retain_trace = tracing_option == "on" or (
                failed and tracing_option == "retain-on-failure"
            )
            if retain_trace:
                trace_path = _build_artifact_test_folder(
                    pytestconfig, request, "trace.zip"
                )
                context.tracing.stop(path=trace_path)
            else:
                context.tracing.stop()

        screenshot_option = pytestconfig.getoption("--screenshot")
        capture_screenshot = screenshot_option == "on" or (
            failed and screenshot_option == "only-on-failure"
        )
        if capture_screenshot:
            for index, page in enumerate(pages):
                human_readable_status = "failed" if failed else "finished"
                screenshot_path = _build_artifact_test_folder(
                    pytestconfig, request, f"test-{human_readable_status}-{index+1}.png"
                )
                try:
                    page.screenshot(timeout=5000, path=screenshot_path)
                except Error:
                    pass

        context.close()

        video_option = pytestconfig.getoption("--video")
        preserve_video = video_option == "on" or (
            failed and video_option == "retain-on-failure"
        )
        if preserve_video:
            for page in pages:
                video = page.video
                if not video:
                    continue
                try:
                    video_path = video.path()
                    file_name = os.path.basename(video_path)
                    video.save_as(
                        path=_build_artifact_test_folder(
                            pytestconfig, request, file_name
                        )
                    )
                except Error:
                    # Silent catch empty videos.
                    pass

    @_task_cache
    def page(self) -> Page:
        context: BrowserContext = self.context
        page = context.new_page()
        return page
