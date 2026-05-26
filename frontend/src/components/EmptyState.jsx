import React from 'react';
import Button from './Button';

const EmptyState = ({ onClear }) => {
  return (
    <div className="col-span-full glass-panel p-12 text-center flex flex-col items-center justify-center animate-fade-in">
      <div className="w-20 h-20 rounded-full bg-slate-800 flex items-center justify-center mb-6 border border-slate-700 shadow-inner">
        <span className="text-4xl">📭</span>
      </div>
      <h3 className="text-2xl font-bold text-white mb-2">No breaches found</h3>
      <p className="text-slate-400 max-w-md mx-auto mb-8">
        We couldn't find any data breaches matching your search criteria in our database. Try adjusting your search terms.
      </p>
      {onClear && (
        <Button variant="secondary" onClick={onClear}>
          Clear Search
        </Button>
      )}
    </div>
  );
};

export default EmptyState;
