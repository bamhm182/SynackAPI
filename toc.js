// Populate the sidebar
//
// This is a script, and not included directly in the page, to control the total size of the book.
// The TOC contains an entry for each page, so if each page includes a copy of the TOC,
// the total size of the page becomes O(n**2).
class MDBookSidebarScrollbox extends HTMLElement {
    constructor() {
        super();
    }
    connectedCallback() {
        this.innerHTML = '<ol class="chapter"><li class="chapter-item "><a href="index.html">Introduction</a></li><li class="chapter-item "><a href="support/index.html">Support</a></li><li class="chapter-item "><a href="tests/index.html">Tests</a></li><li class="chapter-item "><a href="usage/index.html">Usage</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="usage/examples/index.html">Examples</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="usage/examples/check-invisible-missions.html">Check Invisible Missions</a></li><li class="chapter-item "><a href="usage/examples/mission-bot.html">Mission Bot</a></li><li class="chapter-item "><a href="usage/examples/mission-templates.html">Mission Templates</a></li><li class="chapter-item "><a href="usage/examples/register-targets.html">Register Targets</a></li></ol></li><li class="chapter-item "><a href="usage/main-components/index.html">Main Components</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="usage/main-components/files.html">Files</a></li><li class="chapter-item "><a href="usage/main-components/handler.html">Handler</a></li><li class="chapter-item "><a href="usage/main-components/state.html">State</a></li></ol></li><li class="chapter-item "><a href="usage/plugins/index.html">Plugins</a><a class="toggle"><div>❱</div></a></li><li><ol class="section"><li class="chapter-item "><a href="usage/plugins/alerts.html">Alerts</a></li><li class="chapter-item "><a href="usage/plugins/api.html">Api</a></li><li class="chapter-item "><a href="usage/plugins/auth.html">Auth</a></li><li class="chapter-item "><a href="usage/plugins/db.html">Db</a></li><li class="chapter-item "><a href="usage/plugins/debug.html">Debug</a></li><li class="chapter-item "><a href="usage/plugins/duo.html">Duo</a></li><li class="chapter-item "><a href="usage/plugins/missions.html">Missions</a></li><li class="chapter-item "><a href="usage/plugins/notifications.html">Notifications</a></li><li class="chapter-item "><a href="usage/plugins/scratchspace.html">Scratchspace</a></li><li class="chapter-item "><a href="usage/plugins/targets.html">Targets</a></li><li class="chapter-item "><a href="usage/plugins/templates.html">Templates</a></li><li class="chapter-item "><a href="usage/plugins/transactions.html">Transactions</a></li><li class="chapter-item "><a href="usage/plugins/users.html">Users</a></li></ol></li></ol></li></ol>';
        // Set the current, active page, and reveal it if it's hidden
        let current_page = document.location.href.toString();
        if (current_page.endsWith("/")) {
            current_page += "index.html";
        }
        var links = Array.prototype.slice.call(this.querySelectorAll("a"));
        var l = links.length;
        for (var i = 0; i < l; ++i) {
            var link = links[i];
            var href = link.getAttribute("href");
            if (href && !href.startsWith("#") && !/^(?:[a-z+]+:)?\/\//.test(href)) {
                link.href = path_to_root + href;
            }
            // The "index" page is supposed to alias the first chapter in the book.
            if (link.href === current_page || (i === 0 && path_to_root === "" && current_page.endsWith("/index.html"))) {
                link.classList.add("active");
                var parent = link.parentElement;
                if (parent && parent.classList.contains("chapter-item")) {
                    parent.classList.add("expanded");
                }
                while (parent) {
                    if (parent.tagName === "LI" && parent.previousElementSibling) {
                        if (parent.previousElementSibling.classList.contains("chapter-item")) {
                            parent.previousElementSibling.classList.add("expanded");
                        }
                    }
                    parent = parent.parentElement;
                }
            }
        }
        // Track and set sidebar scroll position
        this.addEventListener('click', function(e) {
            if (e.target.tagName === 'A') {
                sessionStorage.setItem('sidebar-scroll', this.scrollTop);
            }
        }, { passive: true });
        var sidebarScrollTop = sessionStorage.getItem('sidebar-scroll');
        sessionStorage.removeItem('sidebar-scroll');
        if (sidebarScrollTop) {
            // preserve sidebar scroll position when navigating via links within sidebar
            this.scrollTop = sidebarScrollTop;
        } else {
            // scroll sidebar to current active section when navigating via "next/previous chapter" buttons
            var activeSection = document.querySelector('#sidebar .active');
            if (activeSection) {
                activeSection.scrollIntoView({ block: 'center' });
            }
        }
        // Toggle buttons
        var sidebarAnchorToggles = document.querySelectorAll('#sidebar a.toggle');
        function toggleSection(ev) {
            ev.currentTarget.parentElement.classList.toggle('expanded');
        }
        Array.from(sidebarAnchorToggles).forEach(function (el) {
            el.addEventListener('click', toggleSection);
        });
    }
}
window.customElements.define("mdbook-sidebar-scrollbox", MDBookSidebarScrollbox);
