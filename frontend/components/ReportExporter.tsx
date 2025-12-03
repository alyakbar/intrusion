'use client'

import { useState } from 'react'
import { FileText, Download, Calendar, FileType, Loader2, CheckCircle, XCircle } from 'lucide-react'

export default function ReportExporter() {
  const [format, setFormat] = useState<'pdf' | 'csv'>('pdf')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [includeCharts, setIncludeCharts] = useState(true)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const handleExport = async () => {
    setLoading(true)
    setMessage(null)

    try {
      const params = new URLSearchParams()
      params.append('format', format)
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      if (format === 'pdf') params.append('include_charts', includeCharts.toString())

      const response = await fetch(`http://localhost:5000/api/reports/generate?${params.toString()}`)
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to generate report')
      }

      // Download the file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `detection_report_${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setMessage({ type: 'success', text: `${format.toUpperCase()} report downloaded successfully!` })
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Failed to generate report' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <FileText className="h-5 w-5 text-blue-500" />
        <h3 className="text-lg font-semibold text-white">Export Report</h3>
      </div>

      <div className="space-y-4">
        {/* Format Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Report Format
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setFormat('pdf')}
              className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg border transition-all ${
                format === 'pdf'
                  ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                  : 'bg-gray-800/50 border-gray-700 text-gray-400 hover:border-gray-600'
              }`}
            >
              <FileType className="h-4 w-4" />
              <span className="font-medium">PDF</span>
            </button>
            <button
              onClick={() => setFormat('csv')}
              className={`flex items-center justify-center gap-2 px-4 py-3 rounded-lg border transition-all ${
                format === 'csv'
                  ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                  : 'bg-gray-800/50 border-gray-700 text-gray-400 hover:border-gray-600'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span className="font-medium">CSV</span>
            </button>
          </div>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Start Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              End Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* PDF Options */}
        {format === 'pdf' && (
          <div className="flex items-center gap-3 p-3 bg-gray-800/30 rounded-lg border border-gray-700">
            <input
              type="checkbox"
              id="include-charts"
              checked={includeCharts}
              onChange={(e) => setIncludeCharts(e.target.checked)}
              className="w-4 h-4 text-blue-500 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2"
            />
            <label htmlFor="include-charts" className="text-sm text-gray-300">
              Include charts and visualizations
            </label>
          </div>
        )}

        {/* Generate Button */}
        <button
          onClick={handleExport}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Generating Report...</span>
            </>
          ) : (
            <>
              <Download className="h-4 w-4" />
              <span>Generate {format.toUpperCase()} Report</span>
            </>
          )}
        </button>

        {/* Status Message */}
        {message && (
          <div
            className={`flex items-center gap-2 p-3 rounded-lg border ${
              message.type === 'success'
                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                : 'bg-red-500/10 border-red-500/30 text-red-400'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="h-4 w-4" />
            ) : (
              <XCircle className="h-4 w-4" />
            )}
            <span className="text-sm">{message.text}</span>
          </div>
        )}

        {/* Info */}
        <div className="text-xs text-gray-400 space-y-1">
          <p>• Leave dates empty to export all detections</p>
          <p>• PDF reports include summary statistics and visualizations</p>
          <p>• CSV reports provide raw data for external analysis</p>
        </div>
      </div>
    </div>
  )
}
