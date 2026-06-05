import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

function confidenceBadge(score) {
  if (score == null) return null
  const num = Number(score)
  
  // Handle timeout/unavailable case
  if (num === -1) {
    return (
      <span className="inline-block bg-slate-600 text-slate-300 text-sm font-bold px-3 py-1 rounded-full">
        Critic unavailable
      </span>
    )
  }
  
  let color = 'bg-green-600'
  if (num < 5) color = 'bg-red-600'
  else if (num < 8) color = 'bg-yellow-500'
  return (
    <span className={`inline-block ${color} text-white text-sm font-bold px-3 py-1 rounded-full`}>
      {num.toFixed(1)} / 10
    </span>
  )
}

export default function ReportViewer({ report, critique }) {
  const handleDownload = () => {
    const blob = new Blob([report ?? ''], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'report.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  const flaggedClaims = critique?.flagged_claims ?? critique?.flaggedClaims ?? []
  const gaps = critique?.gaps ?? []
  const confidence = critique?.confidence_score ?? critique?.confidenceScore ?? null

  return (
    <div className="flex flex-col gap-4 sm:gap-6 w-full animate-fade-in transition-all duration-500">
      {/* Report Section */}
      <div className="bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 sm:px-5 py-3 border-b border-slate-700">
          <h2 className="text-lg font-semibold text-slate-100 tracking-wide">Research Report</h2>
          <button
            onClick={handleDownload}
            disabled={!report}
            className="w-full sm:w-auto flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
          >
            ⬇ Download Report
          </button>
        </div>
        <div className="overflow-y-auto max-h-[60vh] px-4 sm:px-6 py-4 sm:py-5 prose prose-invert prose-slate max-w-none
          prose-headings:text-slate-100 prose-p:text-slate-300 prose-a:text-indigo-400
          prose-code:bg-slate-800 prose-code:text-indigo-300 prose-code:px-1 prose-code:rounded
          prose-pre:bg-slate-800 prose-pre:border prose-pre:border-slate-700
          prose-blockquote:border-indigo-500 prose-blockquote:text-slate-400
          prose-strong:text-slate-200 prose-li:text-slate-300 prose-table:text-slate-300">
          {report ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
          ) : (
            <p className="text-slate-500 italic">No report generated yet.</p>
          )}
        </div>
      </div>

      {/* Critic's Review Panel */}
      {critique && (
        <div className="bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 px-4 sm:px-5 py-3 border-b border-slate-700">
            <h2 className="text-lg font-semibold text-slate-100 tracking-wide">Critic&apos;s Review</h2>
            {confidenceBadge(confidence)}
          </div>
          <div className="px-4 sm:px-6 py-4 sm:py-5 flex flex-col gap-5">
            {/* Confidence label */}
            {confidence != null && (
              <div className="flex items-center gap-2 text-slate-400 text-sm transition-opacity duration-300">
                <span className="font-medium text-slate-300">Confidence Score:</span>
                {confidenceBadge(confidence)}
              </div>
            )}

            {/* Show unavailable message for -1 score */}
            {confidence === -1 && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-400 text-sm">
                The critic stage timed out, but your report is complete and available above.
              </div>
            )}

            {/* Flagged Claims - only show if confidence != -1 */}
            {confidence !== -1 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Flagged Claims
                </h3>
                {flaggedClaims.length > 0 ? (
                  <ul className="flex flex-col gap-1.5">
                    {flaggedClaims.map((claim, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-slate-300 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2"
                      >
                        <span className="mt-0.5 shrink-0">⚠️</span>
                        <span>{claim}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-500 text-sm italic">No flagged claims.</p>
                )}
              </div>
            )}

            {/* Gaps - only show if confidence != -1 */}
            {confidence !== -1 && (
              <div>
                <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">
                  Research Gaps
                </h3>
                {gaps.length > 0 ? (
                  <ul className="flex flex-col gap-1.5">
                    {gaps.map((gap, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-sm text-slate-300 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2"
                      >
                        <span className="mt-0.5 shrink-0">🔍</span>
                        <span>{gap}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-500 text-sm italic">No gaps identified.</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
