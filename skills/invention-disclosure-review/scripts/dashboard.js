'use strict';
const controls = ['search', 'confidence', 'category', 'term-type'].map(id => document.getElementById(id));
const collections = [...document.querySelectorAll('.collection')];
function filterReports() {
  const [search, confidence, category, termType] = controls.map(x => x.value.trim().toLowerCase());
  for (const section of collections) {
    let count = 0;
    const entries = [...section.querySelectorAll('.entry')];
    for (const entry of entries) {
      const match = entry.dataset.search.includes(search)
        && (!confidence || entry.dataset.levels.split(' ').includes(confidence))
        && (!category || entry.dataset.categories.toLowerCase().split(' ').includes(category))
        && (section.id !== 'glossary' || !termType || entry.dataset.type === termType);
      entry.hidden = !match;
      if (match) count++;
    }
    section.querySelector('.count').textContent = `${count} of ${entries.length} entries`;
    section.querySelector('.empty').hidden = count !== 0;
  }
}
document.getElementById('filters').hidden = false;
controls.forEach(control => control.addEventListener('input', filterReports));
document.getElementById('reset').addEventListener('click', () => {
  controls.forEach(control => { control.value = ''; });
  filterReports();
});
// Reveal a linked source or finding even when filters hide it.
function revealAnchor() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target) return;
  if (target.hidden) {
    controls.forEach(control => { control.value = ''; });
    filterReports();
  }
  for (let parent = target.parentElement; parent; parent = parent.parentElement) {
    if (parent.tagName === 'DETAILS') parent.open = true;
  }
  target.scrollIntoView({block: 'start'});
}
window.addEventListener('hashchange', revealAnchor);
if (location.hash) revealAnchor();
document.getElementById('download').addEventListener('click', () => {
  const data = JSON.parse(document.getElementById('review-data').textContent);
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = String(data.review_id || 'invention-review').replace(/[^a-z0-9_-]/gi, '_') + '.json';
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
let printState;
function beforePrint() {
  if (printState) return;
  printState = {details: [...document.querySelectorAll('details')].map(el => [el, el.open]), values: controls.map(el => el.value)};
  printState.details.forEach(([el]) => { el.open = true; });
  controls.forEach(el => { el.value = ''; });
  filterReports();
}
function afterPrint() {
  if (!printState) return;
  printState.details.forEach(([el, open]) => { el.open = open; });
  controls.forEach((el, i) => { el.value = printState.values[i]; });
  printState = null;
  filterReports();
}
window.addEventListener('beforeprint', beforePrint);
window.addEventListener('afterprint', afterPrint);
document.getElementById('print').addEventListener('click', () => { beforePrint(); window.print(); });
filterReports();
