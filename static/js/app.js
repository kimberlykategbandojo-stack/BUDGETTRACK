// ── BudgetTrack App JS ──

// Set today's date as default for the Add Expense date field on page load
document.addEventListener("DOMContentLoaded", function () {

  // Set today's date on the add-expense date field
  const dateField = document.querySelector('form input[name="date"][type="date"]');
  if (dateField && !dateField.value) {
    dateField.value = new Date().toISOString().split("T")[0];
  }

  // ── Populate Edit Modal from data-* attributes ──
  const editModal = document.getElementById("editModal");
  if (editModal) {
    editModal.addEventListener("show.bs.modal", function (event) {
      const btn = event.relatedTarget;

      document.getElementById("edit_id").value       = btn.dataset.id;
      document.getElementById("edit_name").value     = btn.dataset.name;
      document.getElementById("edit_amount").value   = btn.dataset.amount;
      document.getElementById("edit_date").value     = btn.dataset.date;
      document.getElementById("edit_note").value     = btn.dataset.note || "";

      // Set the correct category option
      const catSelect = document.getElementById("edit_category");
      for (let opt of catSelect.options) {
        opt.selected = (opt.value === btn.dataset.category);
      }
    });
  }

});
