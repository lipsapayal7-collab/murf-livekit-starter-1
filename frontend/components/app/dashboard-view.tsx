'use client';

import { useEffect, useState } from 'react';

interface CallStats {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  success_rate: number;
  avg_duration: number;
}

interface CallRecord {
  date_time: string;
  user_id: string;
  channel: string;
  language: string;
  duration: number;
  outcome: string;
  failure_reason: string | null;
  outcome_result: string | null;
}

export function DashboardView() {
  const [stats, setStats] = useState<CallStats>({
    total_calls: 0,
    successful_calls: 0,
    failed_calls: 0,
    success_rate: 0,
    avg_duration: 0,
  });

  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState('');

  const loadDashboard = async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError('');

      const response = await fetch('/api/dashboard', {
        method: 'GET',
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error('Dashboard API failed');
      }

      const data = await response.json();

      if (!data.success && data.error) {
        throw new Error(data.error);
      }

      setStats(
        data.stats || {
          total_calls: 0,
          successful_calls: 0,
          failed_calls: 0,
          success_rate: 0,
          avg_duration: 0,
        }
      );

      setCalls(data.calls || []);

      setLastUpdated(new Date());
    } catch (error) {
      console.error('Dashboard error:', error);

      setError(
        error instanceof Error
          ? error.message
          : 'Unable to load dashboard data'
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(() => {
      loadDashboard();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-slate-100">
      <div className="mx-auto w-full max-w-7xl px-4">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-blue-900">
              📊 Call Performance Dashboard
            </h1>

            <p className="mt-1 text-sm text-slate-600">
              Real-time statistics of Jan Sahay voice calls.
            </p>

            {lastUpdated && (
              <p className="mt-1 text-xs text-slate-500">
                Last updated:{' '}
                {lastUpdated.toLocaleTimeString()}
              </p>
            )}
          </div>

          <button
            type="button"
            onClick={() => loadDashboard(true)}
            disabled={refreshing}
            className={`rounded-lg px-5 py-2 text-sm font-semibold text-white transition ${
              refreshing
                ? 'cursor-not-allowed bg-blue-400'
                : 'bg-blue-700 hover:bg-blue-800 active:scale-95'
            }`}
          >
            {refreshing ? '⟳ Refreshing...' : '🔄 Refresh'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
            ⚠️ {error}
          </div>
        )}

        {/* Statistics */}
        <div className="grid gap-4 md:grid-cols-4">

          <StatCard
            title="TOTAL CALLS"
            value={stats.total_calls}
            description="All connected calls"
            className="border-blue-600"
          />

          <StatCard
            title="SUCCESSFUL CALLS"
            value={stats.successful_calls}
            description="Completed successfully"
            className="border-green-600"
          />

          <StatCard
            title="FAILED CALLS"
            value={stats.failed_calls}
            description="Ended before success"
            className="border-red-600"
          />

          <StatCard
            title="SUCCESS RATE"
            value={`${stats.success_rate}%`}
            description="Overall call success"
            className="border-orange-500"
          />

        </div>

        {/* Analytics */}
        <div className="mt-6 grid gap-6 md:grid-cols-2">

          {/* Success Rate */}
          <div className="rounded-xl bg-white p-6 shadow-sm">

            <h2 className="text-lg font-bold text-blue-900">
              Success Rate
            </h2>

            <div className="flex min-h-[250px] items-center justify-center">

              <div
                className="flex h-48 w-48 items-center justify-center rounded-full"
                style={{
                  background: `conic-gradient(
                    #16a34a ${stats.success_rate}%,
                    #ef4444 ${stats.success_rate}% 100%
                  )`,
                }}
              >

                <div className="flex h-36 w-36 flex-col items-center justify-center rounded-full bg-white">

                  <span className="text-4xl font-bold text-slate-800">
                    {stats.success_rate}%
                  </span>

                  <span className="text-xs uppercase text-slate-500">
                    Success
                  </span>

                </div>

              </div>

            </div>

            <div className="flex justify-center gap-6 text-sm">

              <span className="text-green-600">
                ● Success
              </span>

              <span className="text-red-500">
                ● Failed
              </span>

            </div>

          </div>

          {/* Call Summary */}
          <div className="rounded-xl bg-white p-6 shadow-sm">

            <h2 className="text-lg font-bold text-blue-900">
              Call Summary
            </h2>

            <div className="mt-6 space-y-5">

              <ProgressRow
                label="Successful"
                value={stats.successful_calls}
                total={stats.total_calls}
              />

              <ProgressRow
                label="Failed"
                value={stats.failed_calls}
                total={stats.total_calls}
              />

              <div className="rounded-lg bg-slate-50 p-4">

                <p className="text-sm text-slate-500">
                  Average Call Duration
                </p>

                <p className="mt-1 text-2xl font-bold text-orange-600">
                  {stats.avg_duration}s
                </p>

              </div>

            </div>

          </div>

        </div>

        {/* Recent Call History */}
        <div className="mt-6 rounded-xl bg-white p-6 shadow-sm">

          <div className="mb-5 flex items-center justify-between">

            <div>
              <h2 className="text-lg font-bold text-blue-900">
                📞 Recent Call History
              </h2>

              <p className="text-sm text-slate-500">
                Showing recent calls from database
              </p>
            </div>

            <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">
              ● Live Data
            </span>

          </div>

          {loading ? (

            <div className="py-10 text-center text-slate-500">
              Loading call data...
            </div>

          ) : calls.length === 0 ? (

            <div className="py-10 text-center text-slate-500">
              No calls recorded yet.
            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-left text-sm">

                <thead>

                  <tr className="border-b bg-slate-50">

                    <th className="p-3">
                      DATE & TIME
                    </th>

                    <th className="p-3">
                      USER ID
                    </th>

                    <th className="p-3">
                      CHANNEL
                    </th>

                    <th className="p-3">
                      LANGUAGE
                    </th>

                    <th className="p-3">
                      DURATION
                    </th>

                    <th className="p-3">
                      OUTCOME
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {calls.map((call, index) => (

                    <tr
                      key={`${call.date_time}-${index}`}
                      className="border-b last:border-0"
                    >

                      <td className="p-3 text-slate-600">
                        {new Date(
                          call.date_time
                        ).toLocaleString()}
                      </td>

                      <td className="p-3 font-medium">
                        {call.user_id}
                      </td>

                      <td className="p-3">

                        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                          {call.channel}
                        </span>

                      </td>

                      <td className="p-3">
                        {call.language}
                      </td>

                      <td className="p-3">
                        {call.duration}s
                      </td>

                      <td className="p-3">

                        {call.outcome === 'Success' ? (

                          <span className="font-semibold text-green-600">
                            ● Success
                          </span>

                        ) : (

                          <span className="font-semibold text-red-600">

                            ● Failed

                            {call.failure_reason
                              ? ` (${call.failure_reason})`
                              : ''}

                          </span>

                        )}

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  description,
  className,
}: {
  title: string;
  value: string | number;
  description: string;
  className: string;
}) {
  return (
    <div
      className={`rounded-xl border-t-4 bg-white p-5 shadow-sm ${className}`}
    >

      <p className="text-xs font-bold tracking-wide text-slate-500">
        {title}
      </p>

      <p className="mt-3 text-4xl font-bold text-slate-900">
        {value}
      </p>

      <p className="mt-2 text-xs text-slate-500">
        {description}
      </p>

    </div>
  );
}

function ProgressRow({
  label,
  value,
  total,
}: {
  label: string;
  value: number;
  total: number;
}) {
  const percentage =
    total > 0
      ? Math.round((value / total) * 100)
      : 0;

  return (
    <div>

      <div className="mb-2 flex justify-between text-sm">

        <span className="font-medium">
          {label}
        </span>

        <span className="text-slate-500">
          {value} calls ({percentage}%)
        </span>

      </div>

      <div className="h-3 overflow-hidden rounded-full bg-slate-100">

        <div
          className="h-full rounded-full bg-blue-600 transition-all"
          style={{
            width: `${percentage}%`,
          }}
        />

      </div>

    </div>
  );
}
