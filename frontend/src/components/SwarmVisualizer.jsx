import React from 'react';

const agents = [
  { icon: '🧠', label: 'Planner', description: 'Plans sub-topics' },
  { icon: '🔍', label: 'Search Agents', description: 'Searches the web' },
  { icon: '📄', label: 'Reader Agents', description: 'Reads sources' },
  { icon: '✍️', label: 'Synthesis', description: 'Synthesizes report' },
  { icon: '✅', label: 'Critic', description: 'Reviews quality' },
];

const backendStatusConfig = {
  sleeping: {
    badge: 'Sleeping',
    badgeClass: 'bg-slate-600 text-slate-300',
    cardClass: 'border-slate-600 bg-slate-800',
    iconClass: 'opacity-40',
  },
  waking: {
    badge: 'Waking up',
    badgeClass: 'bg-amber-400 text-amber-950 animate-pulse',
    cardClass: 'border-amber-400 bg-slate-800 shadow-[0_0_16px_2px_rgba(245,158,11,0.45)]',
    iconClass: 'opacity-100 animate-pulse',
  },
  ready: {
    badge: 'Ready',
    badgeClass: 'bg-green-500 text-green-900',
    cardClass: 'border-green-500 bg-slate-800',
    iconClass: 'opacity-100',
  },
};

const getStatus = (index, activeStep) => {
  if (index < activeStep) return 'done';
  if (index === activeStep) return 'running';
  return 'waiting';
};

const statusConfig = {
  waiting: {
    badge: 'Waiting',
    badgeClass: 'bg-slate-600 text-slate-300',
    cardClass: 'border-slate-600 bg-slate-800',
    iconClass: 'opacity-40',
  },
  running: {
    badge: 'Running',
    badgeClass: 'bg-yellow-500 text-yellow-900 animate-pulse',
    cardClass: 'border-yellow-400 bg-slate-800 shadow-[0_0_16px_2px_rgba(234,179,8,0.45)]',
    iconClass: 'opacity-100',
  },
  done: {
    badge: 'Done',
    badgeClass: 'bg-green-500 text-green-900',
    cardClass: 'border-green-500 bg-slate-800',
    iconClass: 'opacity-100',
  },
};

const SwarmVisualizer = ({ activeStep = -1, backendStatus = 'sleeping' }) => {
  const backendConfig = backendStatusConfig[backendStatus] || backendStatusConfig.sleeping;

  return (
    <div className="w-full py-2 sm:py-4 animate-fade-in transition-all duration-500">
      <p className="text-slate-400 text-xs font-semibold uppercase tracking-widest mb-4 text-center">
        Agent Pipeline
      </p>
      <div className="flex items-center justify-center gap-2 sm:gap-0 flex-wrap">
        <React.Fragment key="backend">
          <div
            className={`flex flex-col items-center justify-between w-[calc(50%-0.5rem)] sm:w-28 min-h-[110px] sm:min-h-[120px] p-2.5 sm:p-3 rounded-xl border-2 transition-all duration-500 ${backendConfig.cardClass}`}
          >
            <span className={`text-3xl leading-none transition-opacity duration-300 ${backendConfig.iconClass}`}>
              💤
            </span>

            <div className="text-center mt-1">
              <p className="text-white text-xs font-semibold leading-tight">Backend</p>
              <p className="text-slate-500 text-[10px] leading-tight mt-0.5">Wakes the swarm</p>
            </div>

            <span
              className={`mt-2 inline-block text-[10px] font-bold px-2 py-0.5 rounded-full transition-colors duration-300 ${backendConfig.badgeClass}`}
            >
              {backendConfig.badge}
            </span>
          </div>

          <div className="hidden sm:flex items-center mx-1 transition-colors duration-500">
            <div
              className={`w-5 h-0.5 transition-colors duration-500 ${
                backendStatus === 'ready' ? 'bg-green-500' : backendStatus === 'waking' ? 'bg-amber-400' : 'bg-slate-600'
              }`}
            />
            <svg
              className={`w-3 h-3 transition-colors duration-500 ${
                backendStatus === 'ready' ? 'text-green-500' : backendStatus === 'waking' ? 'text-amber-400' : 'text-slate-600'
              }`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </div>
        </React.Fragment>

        {agents.map((agent, index) => {
          const status = getStatus(index, activeStep);
          const config = statusConfig[status];

          return (
            <React.Fragment key={agent.label}>
              {/* Agent Card */}
              <div
                className={`flex flex-col items-center justify-between w-[calc(50%-0.5rem)] sm:w-28 min-h-[110px] sm:min-h-[120px] p-2.5 sm:p-3 rounded-xl border-2 transition-all duration-500 ${config.cardClass}`}
              >
                {/* Icon */}
                <span className={`text-3xl leading-none transition-opacity duration-300 ${config.iconClass}`}>
                  {agent.icon}
                </span>

                {/* Label */}
                <div className="text-center mt-1">
                  <p className="text-white text-xs font-semibold leading-tight">{agent.label}</p>
                  <p className="text-slate-500 text-[10px] leading-tight mt-0.5">{agent.description}</p>
                </div>

                {/* Status Badge */}
                <span
                  className={`mt-2 inline-block text-[10px] font-bold px-2 py-0.5 rounded-full transition-colors duration-300 ${config.badgeClass}`}
                >
                  {config.badge}
                </span>
              </div>

              {/* Connector Arrow (between cards) */}
              {index < agents.length - 1 && (
                <div className="hidden sm:flex items-center mx-1 transition-colors duration-500">
                  <div
                    className={`w-5 h-0.5 transition-colors duration-500 ${
                      index < activeStep ? 'bg-green-500' : 'bg-slate-600'
                    }`}
                  />
                  <svg
                    className={`w-3 h-3 transition-colors duration-500 ${
                      index < activeStep ? 'text-green-500' : 'text-slate-600'
                    }`}
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default SwarmVisualizer;
