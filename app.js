(function () {
    const body = document.body;
    const toastBox = document.getElementById("toast");
    const modal = document.getElementById("modal");
    const modalTitle = document.getElementById("modal-title");
    const modalBody = document.getElementById("modal-body");
    const modalClose = document.getElementById("modal-close");
    const globalSearch = document.getElementById("global-search");
    const newRecordButton = document.getElementById("new-record");

    function showToast(message) {
        if (!toastBox || !message) return;
        toastBox.textContent = message;
        toastBox.classList.add("show");
        window.clearTimeout(showToast.timer);
        showToast.timer = window.setTimeout(() => toastBox.classList.remove("show"), 3200);
    }

    function openModal(title, content) {
        if (!modal || !modalTitle || !modalBody) return;
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        modal.classList.add("show");
        modal.setAttribute("aria-hidden", "false");
    }

    function closeModal() {
        if (!modal) return;
        modal.classList.remove("show");
        modal.setAttribute("aria-hidden", "true");
    }

    function routeForSearch(term) {
        const value = term.toLowerCase();
        if (value.includes("loan") || value.startsWith("ln-")) return body.dataset.loansUrl;
        if (value.includes("acc") || value.includes("account")) return body.dataset.accountsUrl;
        if (value.includes("transaction") || value.includes("deposit") || value.includes("withdraw")) return body.dataset.transactionsUrl;
        return body.dataset.membersUrl;
    }

    function filterVisibleTables(term) {
        const normalized = term.trim().toLowerCase();
        let matched = 0;
        document.querySelectorAll(".table-wrap tbody tr").forEach(row => {
            const isEmptyRow = row.children.length === 1;
            const visible = !normalized || row.textContent.toLowerCase().includes(normalized) || isEmptyRow;
            row.classList.toggle("is-hidden", !visible);
            if (visible && !isEmptyRow) matched += 1;
        });
        return matched;
    }

    function submitGlobalSearch() {
        if (!globalSearch) return;
        const term = globalSearch.value.trim();
        if (!term) {
            showToast("Type a member, account, loan, or transaction to search.");
            return;
        }

        const visibleRows = document.querySelectorAll(".table-wrap tbody tr").length;
        if (visibleRows) {
            const matched = filterVisibleTables(term);
            showToast(`${matched} matching row${matched === 1 ? "" : "s"} shown on this page.`);
            return;
        }

        const target = routeForSearch(term);
        if (target) window.location.href = `${target}?q=${encodeURIComponent(term)}`;
    }

    function setupGlobalSearch() {
        if (!globalSearch) return;

        globalSearch.addEventListener("input", event => {
            if (document.querySelector(".table-wrap tbody")) {
                filterVisibleTables(event.target.value);
            }
        });
        globalSearch.addEventListener("keydown", event => {
            if (event.key === "Enter") {
                event.preventDefault();
                submitGlobalSearch();
            }
        });
    }

    function setupTopbarActions() {
        const printButton = document.querySelector("[data-action='print']");
        const notificationButton = document.querySelector("[data-action='notifications']");

        if (printButton) {
            printButton.addEventListener("click", () => window.print());
        }

        if (notificationButton) {
            notificationButton.addEventListener("click", () => {
                const appliedLoans = Array.from(document.querySelectorAll("td")).filter(cell => cell.textContent.trim() === "Applied").length;
                const defaultedLoans = Array.from(document.querySelectorAll("td")).filter(cell => cell.textContent.trim() === "Defaulted").length;
                const messages = Array.from(document.querySelectorAll(".auth-messages p")).map(item => item.textContent.trim());
                const rows = [
                    `<div class="list-item"><strong>${appliedLoans} loans awaiting approval</strong><span>Open Loans to approve, reject, or disburse eligible records.</span></div>`,
                    `<div class="list-item"><strong>${defaultedLoans} defaulted loan rows visible</strong><span>Use Reports or Loans to review arrears follow-up.</span></div>`,
                    ...messages.map(message => `<div class="list-item"><strong>Recent system message</strong><span>${message}</span></div>`),
                ];
                openModal("Notifications", `<div class="stack-list">${rows.join("")}</div>`);
            });
        }

        if (newRecordButton) {
            newRecordButton.addEventListener("click", () => {
                const target = body.dataset.currentCreateUrl || body.dataset.membersUrl?.replace(/\/$/, "/new/");
                if (target) window.location.href = target;
            });
        }
    }

    function setupMessages() {
        document.querySelectorAll(".auth-messages p").forEach(message => {
            showToast(message.textContent.trim());
        });
    }

    function setupForms() {
        document.querySelectorAll("form").forEach(form => {
            if (form.id === "loan-calculator-form") return;
            const submitButton = form.querySelector("button[type='submit']");

            form.addEventListener("input", () => form.classList.add("form-dirty"), { once: true });
            form.addEventListener("submit", () => {
                if (submitButton) {
                    submitButton.dataset.originalText = submitButton.textContent;
                    submitButton.textContent = "Saving...";
                    submitButton.disabled = true;
                }
            });
        });

        document.querySelectorAll("input, select, textarea").forEach(field => {
            field.addEventListener("focus", () => field.closest("label")?.classList.add("field-active"));
            field.addEventListener("blur", () => field.closest("label")?.classList.remove("field-active"));
        });
    }

    function setupRows() {
        document.querySelectorAll(".table-wrap tbody tr").forEach(row => {
            row.addEventListener("click", event => {
                if (event.target.closest("a, button, input, select")) return;
                document.querySelectorAll(".table-wrap tr.row-selected").forEach(item => item.classList.remove("row-selected"));
                row.classList.add("row-selected");
            });
        });
    }

    function setupModal() {
        modalClose?.addEventListener("click", closeModal);
        modal?.addEventListener("click", event => {
            if (event.target === modal) closeModal();
        });
        document.addEventListener("keydown", event => {
            if (event.key === "Escape") closeModal();
        });
    }

    function setupLoanCalculator() {
        const toggle = document.getElementById("calculator-toggle");
        const panel = document.getElementById("calculator-panel");
        const close = document.getElementById("calculator-close");
        const form = document.getElementById("loan-calculator-form");
        const results = document.getElementById("calculator-results");
        if (!toggle || !panel || !form || !results) return;

        const money = new Intl.NumberFormat("en-UG", {
            style: "currency",
            currency: "UGX",
            maximumFractionDigits: 0,
        });

        function setOpen(isOpen) {
            panel.classList.toggle("show", isOpen);
            panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
        }

        toggle.addEventListener("click", () => setOpen(!panel.classList.contains("show")));
        close?.addEventListener("click", () => setOpen(false));

        form.addEventListener("submit", event => {
            event.preventDefault();
            const salary = Number(document.getElementById("calculator-salary")?.value || 0);
            const annualRate = Number(document.getElementById("calculator-interest")?.value || 0) / 100;
            const months = Number(document.getElementById("calculator-period")?.value || 0);
            if (!salary || !months) {
                showToast("Enter salary and loan period to calculate.");
                return;
            }

            const monthlyLimit = salary * 0.48;
            const monthlyRate = annualRate / 12;
            const principal = monthlyRate
                ? monthlyLimit * ((Math.pow(1 + monthlyRate, months) - 1) / (monthlyRate * Math.pow(1 + monthlyRate, months)))
                : monthlyLimit * months;
            const totalPayable = monthlyLimit * months;
            const totalInterest = Math.max(0, totalPayable - principal);

            document.getElementById("calculator-max-loan").textContent = money.format(principal);
            document.getElementById("calculator-monthly-payment").textContent = money.format(monthlyLimit);
            document.getElementById("calculator-total-interest").textContent = money.format(totalInterest);
            document.getElementById("calculator-total-payable").textContent = money.format(totalPayable);
            results.classList.add("show");
        });
    }

    setupGlobalSearch();
    setupTopbarActions();
    setupMessages();
    setupForms();
    setupRows();
    setupModal();
    setupLoanCalculator();
})();
