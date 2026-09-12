import React, { useEffect, useState } from 'react';
import FilterBar from './components/FilterBar';
import DiscrepancyTable from './components/DiscrepancyTable';

const API = import.meta.env.VITE_API_URL || '/api';

export default function App() {
  const [orgs, setOrgs] = useState([]);
  const [org, setOrg] = useState('');
  const [reason, setReason] = useState('ALL');
  const [sort, setSort] = useState('asc');
  const [rows, setRows] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${API}/organizations/`)
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.error || 'Failed to load organizations.'
          );
        }

        setOrgs(data);

        if (data.length > 0) {
          setOrg(String(data[0].id));
        }
      })
      .catch((err) => {
        setError(
          err.message || 'Backend is not running.'
        );
      });
  }, []);

  useEffect(() => {
    if (!org) return;

    setError('');

    const params = new URLSearchParams({
      org_id: org,
      sort,
    });

    if (reason !== 'ALL') {
      params.set('reason', reason);
    }

    fetch(`${API}/discrepancies/?${params.toString()}`)
      .then(async (response) => {
        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.error || 'Request failed.'
          );
        }

        setRows(data);
      })
      .catch((err) => {
        setError(
          err.message || 'Failed to load discrepancies.'
        );
        setRows([]);
      });
  }, [org, reason, sort]);

  return (
    <main>
      <header>
        <h1>Reconciliation Dashboard</h1>

        <p>
          Cross-system discrepancies, scoped to one organization.
        </p>
      </header>

      <FilterBar
        orgs={orgs}
        org={org}
        setOrg={setOrg}
        reason={reason}
        setReason={setReason}
        sort={sort}
        setSort={setSort}
      />

      {error && (
        <p className="error">
          {error}
        </p>
      )}

      <p className="count">
        {rows.length} disagreement
        {rows.length === 1 ? '' : 's'}
      </p>

      <DiscrepancyTable items={rows} />
    </main>
  );
}