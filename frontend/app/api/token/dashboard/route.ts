import { NextResponse } from 'next/server';
import Database from 'better-sqlite3';
import path from 'path';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  let db: Database.Database | null = null;

  try {
    const dbPath = path.resolve(
      process.cwd(),
      '..',
      'backend',
      'financial_users.db'
    );

    db = new Database(dbPath, {
      readonly: true,
    });

    const totalRow = db
      .prepare(`
        SELECT COUNT(*) AS count
        FROM calls
      `)
      .get() as { count: number };

    const successRow = db
      .prepare(`
        SELECT COUNT(*) AS count
        FROM calls
        WHERE TRIM(outcome) = 'Success'
      `)
      .get() as { count: number };

    const failedRow = db
      .prepare(`
        SELECT COUNT(*) AS count
        FROM calls
        WHERE TRIM(outcome) = 'Failed'
      `)
      .get() as { count: number };

    const durationRow = db
      .prepare(`
        SELECT AVG(duration) AS average
        FROM calls
      `)
      .get() as { average: number | null };

    const calls = db
      .prepare(`
        SELECT
          created_at AS date_time,
          user_id,
          channel,
          language,
          duration,
          outcome,
          failure_reason,
          outcome_result
        FROM calls
        ORDER BY call_id DESC
        LIMIT 10
      `)
      .all();

    const totalCalls = totalRow.count || 0;
    const successfulCalls = successRow.count || 0;
    const failedCalls = failedRow.count || 0;

    const avgDuration = durationRow.average || 0;

    const successRate =
      totalCalls > 0
        ? Math.round((successfulCalls / totalCalls) * 100)
        : 0;

    return NextResponse.json({
      success: true,

      stats: {
        total_calls: totalCalls,
        successful_calls: successfulCalls,
        failed_calls: failedCalls,
        success_rate: successRate,
        avg_duration: Number(avgDuration.toFixed(2)),
      },

      calls,
    });
  } catch (error) {
    console.error('Dashboard database error:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Unable to load call dashboard data',
        details:
          error instanceof Error
            ? error.message
            : 'Unknown error',
      },
      { status: 500 }
    );
  } finally {
    if (db) {
      db.close();
    }
  }
}
