import React from 'react';

const reasons = [
  ['ALL', 'All reasons'],
  ['MISSING_IN_SYSTEM_B', 'Missing in System B'],
  ['ORPHAN_IN_SYSTEM_B', 'Orphan in System B'],
  ['DUPLICATE_IN_SYSTEM_B', 'Duplicate in System B'],
  ['VALUE_MISMATCH', 'Value mismatch'],
];

export default function FilterBar({ orgs, org, setOrg, reason, setReason, sort, setSort }) {
  return (
    <section className="controls">
      <label>
        Organization
        <select value={org} onChange={(e) => setOrg(e.target.value)}>
          {orgs.map((item) => (
            <option key={item.id} value={item.id}>{item.name}</option>
          ))}
        </select>
      </label>

      <label>
        Reason
        <select value={reason} onChange={(e) => setReason(e.target.value)}>
          {reasons.map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </label>

      <button onClick={() => setSort(sort === 'asc' ? 'desc' : 'asc')}>
        Sort value: {sort === 'asc' ? 'Ascending' : 'Descending'}
      </button>
    </section>
  );
}
