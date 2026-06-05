import React, { useState } from 'react';

const InputPanel = ({ onSubmit, isLoading = false, isPreparingBackend = false, warmupBanner }) => {
  const [question, setQuestion] = useState('');

  const showWarmupBanner = Boolean(warmupBanner?.visible);
  const isBackendReady = warmupBanner?.phase === 'ready';

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim() || isLoading || isPreparingBackend) return;

    try {
      await onSubmit(question.trim());
      setQuestion('');
    } catch (error) {
      console.error('Error submitting research question:', error);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-sm bg-opacity-80 animate-fade-in transition-all duration-500">
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-5 sm:px-8 sm:py-6">
        <h2 className="text-xl sm:text-2xl font-bold text-white">Launch Your Research</h2>
        <p className="text-blue-100 mt-1 text-sm sm:text-base">
          Enter your research question and let the swarm generate a comprehensive report.
        </p>
      </div>

      <div className="p-4 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="question" className="block text-sm font-semibold text-slate-300 mb-3">
              Research Question
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isLoading || isPreparingBackend}
              placeholder="What would you like to research?"
              className="w-full h-28 sm:h-32 px-4 py-3 bg-slate-800 text-white placeholder-slate-500 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          <div
            className={`overflow-hidden transition-all duration-500 ease-out ${
              showWarmupBanner ? 'max-h-40 opacity-100 translate-y-0' : 'max-h-0 opacity-0 -translate-y-2'
            }`}
            aria-live="polite"
          >
            <div className="rounded-xl border border-amber-300/70 bg-[#F59E0B] px-4 py-3 text-slate-900 shadow-lg">
              <div className="flex items-start gap-3">
                <span className="text-2xl leading-none animate-pulse" aria-hidden="true">
                  🔥
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-sm sm:text-base font-bold">
                    {isBackendReady
                      ? 'Swarm is awake! Starting research...'
                      : 'Waking up the swarm... this may take 30–50 seconds on first load.'}
                  </p>
                  <div className="mt-3 h-2.5 w-full overflow-hidden rounded-full bg-amber-200/80">
                    <div
                      className="h-full rounded-full bg-amber-700 transition-[width] duration-200 ease-linear"
                      style={{ width: `${warmupBanner?.progress ?? 0}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={!question.trim() || isLoading || isPreparingBackend}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-60"
          >
            {isPreparingBackend ? 'Waking Swarm...' : isLoading ? 'Running Swarm...' : 'Start Research'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default InputPanel;
