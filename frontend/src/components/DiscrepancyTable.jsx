import React from 'react';

export default function DiscrepancyTable({ items }) {
  return (
    <div>
      <table
        border="1"
        cellPadding="8"
        style={{
          width: '100%',
          marginTop: '1rem',
          borderCollapse: 'collapse'
        }}
      >
        <thead>
          <tr>
            <th>Reason</th>
            <th>Record / Ref</th>
            <th>Location</th>
            <th>Organization</th>
            <th>System A</th>
            <th>System B</th>
          </tr>
        </thead>

        <tbody>
          {items.length === 0 ? (
            <tr>
              <td colSpan="6">No disagreements for this filter.</td>
            </tr>
          ) : (
            items.map((row, idx) => (
              <tr key={`${row.record_id}-${row.reason}-${idx}`}>
                <td>
                  <strong>{row.reason}</strong>
                </td>
                <td>{row.record_id ?? row.record_ref ?? '—'}</td>
                <td>{row.location_id ?? '—'}</td>
                <td>{row.org_id ?? '—'}</td>
                <td>{row.val_a ?? '—'}</td>
                <td>{row.val_b ?? '—'}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}