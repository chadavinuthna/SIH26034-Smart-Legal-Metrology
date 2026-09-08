import React from 'react';
import { Image as ImageIcon, Trash2, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export default function ImagePreviewCard({ imageSrc, fileInfo, imageMetadata, onRemove, onReplace }) {
  if (!imageSrc) return null;

  const quality = imageMetadata?.quality_label || 'GOOD';
  const textVis = imageMetadata?.text_visibility || 'CLEAR';

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
          <ImageIcon size={15} className="text-blue-800" />
          <span>Uploaded Package Image</span>
        </div>
        <div className="flex items-center gap-2">
          {onReplace && (
            <button
              onClick={onReplace}
              className="text-xs font-semibold text-slate-600 hover:text-blue-800 flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-200/60 transition-colors"
            >
              <RefreshCw size={12} />
              Replace
            </button>
          )}
          {onRemove && (
            <button
              onClick={onRemove}
              className="text-xs font-semibold text-rose-600 hover:text-rose-800 flex items-center gap-1 px-2 py-1 rounded hover:bg-rose-50 transition-colors"
            >
              <Trash2 size={12} />
              Remove
            </button>
          )}
        </div>
      </div>

      {/* Image display */}
      <div className="p-4 flex flex-col md:flex-row gap-4 items-center">
        <div className="relative w-full md:w-60 h-48 bg-slate-900 rounded-lg overflow-hidden flex items-center justify-center border border-slate-200 shrink-0">
          <img
            src={imageSrc}
            alt="Package Label"
            className="w-full h-full object-contain"
          />
        </div>

        {/* Metadata Details */}
        <div className="flex-1 w-full space-y-3">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-500 block">Filename</span>
              <span className="font-semibold text-slate-800 truncate block mt-0.5" title={fileInfo?.name || 'package_label.jpg'}>
                {fileInfo?.name || 'package_label.jpg'}
              </span>
            </div>
            <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-500 block">Dimensions</span>
              <span className="font-mono font-semibold text-slate-800 block mt-0.5">
                {imageMetadata?.width ? `${imageMetadata.width} × ${imageMetadata.height} px` : 'Approx. 1200 × 800 px'}
              </span>
            </div>
          </div>

          {/* Simple Quality Indicators */}
          <div className="p-3 bg-blue-50/50 rounded-lg border border-blue-100 flex items-center justify-between">
            <div>
              <span className="text-[11px] uppercase tracking-wider text-slate-500 font-bold block">
                Image Quality
              </span>
              <span className="text-xs font-bold text-emerald-800 flex items-center gap-1 mt-0.5">
                <CheckCircle2 size={13} className="text-emerald-600" />
                {quality}
              </span>
            </div>

            <div>
              <span className="text-[11px] uppercase tracking-wider text-slate-500 font-bold block">
                Text Visibility
              </span>
              <span className="text-xs font-bold text-blue-900 flex items-center gap-1 mt-0.5">
                <CheckCircle2 size={13} className="text-blue-600" />
                {textVis}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
