import React, { useState } from 'react';

const InputPanel = ({ onSubmit, isLoading = false }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim() || isLoading) return;

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
              disabled={isLoading}
              placeholder="What would you like to research?"
              className="w-full h-28 sm:h-32 px-4 py-3 bg-slate-800 text-white placeholder-slate-500 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
            />
          </div>

          <button
            type="submit"
            disabled={!question.trim() || isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 disabled:opacity-60"
          >
            {isLoading ? 'Running Swarm...' : 'Start Research'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default InputPanel;
