'use client'

import { useState } from 'react'
import { Filter, Code, X } from 'lucide-react'

interface FilterPreset {
  name: string
  filter: string
  description: string
}

const FILTER_PRESETS: FilterPreset[] = [
  { name: 'Web Traffic', filter: 'tcp and (port 80 or port 443)', description: 'HTTP/HTTPS traffic' },
  { name: 'DNS Queries', filter: 'udp and port 53', description: 'DNS resolution requests' },
  { name: 'SSH Connections', filter: 'tcp and port 22', description: 'Secure shell traffic' },
  { name: 'Database Traffic', filter: 'tcp and (port 3306 or port 5432 or port 1433)', description: 'MySQL, PostgreSQL, MSSQL' },
  { name: 'Email Traffic', filter: 'tcp and (port 25 or port 587 or port 993)', description: 'SMTP, IMAP traffic' },
  { name: 'ICMP Traffic', filter: 'icmp', description: 'Ping and network diagnostics' },
  { name: 'Large Packets', filter: 'length > 1000', description: 'Packets larger than 1KB' },
  { name: 'Local Network', filter: 'net 192.168.0.0/16', description: 'Private network traffic' },
]

interface PacketFilterProps {
  onFilterApply?: (filter: string) => void
}

export default function PacketFilterBuilder({ onFilterApply }: PacketFilterProps) {
  const [customFilter, setCustomFilter] = useState('')
  const [selectedPreset, setSelectedPreset] = useState<FilterPreset | null>(null)
  const [activeFilter, setActiveFilter] = useState<string>('')

  const applyFilter = (filter: string) => {
    setActiveFilter(filter)
    if (onFilterApply) {
      onFilterApply(filter)
    }
  }

  const handlePresetClick = (preset: FilterPreset) => {
    setSelectedPreset(preset)
    setCustomFilter(preset.filter)
  }

  const handleApplyCustom = () => {
    if (customFilter.trim()) {
      applyFilter(customFilter)
    }
  }

  const clearFilter = () => {
    setActiveFilter('')
    setCustomFilter('')
    setSelectedPreset(null)
    if (onFilterApply) {
      onFilterApply('')
    }
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-semibold text-white">Packet Filter</h3>
        </div>
        {activeFilter && (
          <button
            onClick={clearFilter}
            className="flex items-center gap-1 px-3 py-1 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm transition-colors"
          >
            <X className="h-3 w-3" />
            Clear Filter
          </button>
        )}
      </div>

      {/* Active Filter Display */}
      {activeFilter && (
        <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <div className="flex items-center gap-2 text-sm">
            <Code className="h-4 w-4 text-blue-400" />
            <span className="text-gray-400">Active Filter:</span>
            <code className="text-blue-400 font-mono">{activeFilter}</code>
          </div>
        </div>
      )}

      {/* Filter Presets */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Quick Filters
        </label>
        <div className="grid grid-cols-2 gap-2">
          {FILTER_PRESETS.map((preset) => (
            <button
              key={preset.name}
              onClick={() => {
                handlePresetClick(preset)
                applyFilter(preset.filter)
              }}
              className={`text-left p-3 rounded-lg border transition-all ${
                activeFilter === preset.filter
                  ? 'bg-blue-500/20 border-blue-500 text-blue-400'
                  : 'bg-gray-800/50 border-gray-700 text-gray-300 hover:border-gray-600'
              }`}
            >
              <div className="font-medium text-sm mb-1">{preset.name}</div>
              <div className="text-xs text-gray-400">{preset.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Custom Filter (BPF Syntax)
        </label>
        <div className="space-y-2">
          <input
            type="text"
            value={customFilter}
            onChange={(e) => setCustomFilter(e.target.value)}
            placeholder="e.g., tcp and port 80"
            className="w-full px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
          />
          <button
            onClick={handleApplyCustom}
            disabled={!customFilter.trim()}
            className="w-full px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            Apply Custom Filter
          </button>
        </div>
      </div>

      {/* Syntax Help */}
      <div className="mt-6 p-4 bg-gray-800/30 rounded-lg border border-gray-700">
        <div className="text-sm text-gray-300 font-medium mb-2">Filter Syntax Examples:</div>
        <div className="space-y-1 text-xs text-gray-400 font-mono">
          <div><span className="text-blue-400">tcp port 80</span> - TCP traffic on port 80</div>
          <div><span className="text-blue-400">host 192.168.1.1</span> - Traffic from/to specific host</div>
          <div><span className="text-blue-400">net 10.0.0.0/8</span> - Traffic from subnet</div>
          <div><span className="text-blue-400">length &gt; 500</span> - Packets larger than 500 bytes</div>
          <div><span className="text-blue-400">tcp and not port 22</span> - TCP except SSH</div>
        </div>
      </div>
    </div>
  )
}
