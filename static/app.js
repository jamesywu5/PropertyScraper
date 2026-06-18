const filterInput = document.querySelector("#listingFilter");
const table = document.querySelector("#listingsTable");

if (filterInput && table) {
  filterInput.addEventListener("input", () => {
    const query = filterInput.value.toLowerCase();

    table.querySelectorAll("tbody tr").forEach((row) => {
      row.hidden = !row.textContent.toLowerCase().includes(query);
    });
  });
}

if (table) {
  table.querySelectorAll("th").forEach((header, index) => {
    header.addEventListener("click", () => sortTable(table, index, header.dataset.type));
  });
}

function sortTable(tableElement, index, type) {
  const tbody = tableElement.querySelector("tbody");
  const rows = Array.from(tbody.querySelectorAll("tr")).filter(
    (row) => !row.querySelector(".empty-table")
  );
  const direction = tableElement.dataset.sortDirection === "asc" ? "desc" : "asc";

  rows.sort((a, b) => {
    const aCell = a.children[index];
    const bCell = b.children[index];
    const aValue = aCell.dataset.value || aCell.textContent.trim();
    const bValue = bCell.dataset.value || bCell.textContent.trim();

    if (type === "number") {
      const aNumber = Number.parseFloat(aValue) || Number.POSITIVE_INFINITY;
      const bNumber = Number.parseFloat(bValue) || Number.POSITIVE_INFINITY;
      return direction === "asc" ? aNumber - bNumber : bNumber - aNumber;
    }

    return direction === "asc"
      ? aValue.localeCompare(bValue)
      : bValue.localeCompare(aValue);
  });

  tableElement.dataset.sortDirection = direction;
  rows.forEach((row) => tbody.appendChild(row));
}
