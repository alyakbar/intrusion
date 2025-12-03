'use client'

import { Shield, ArrowLeft } from 'lucide-react'
import { useRouter } from 'next/navigation'
import ThreatIntelligence from '@/components/ThreatIntelligence'
import ReportExporter from '@/components/ReportExporter'
import PacketFilterBuilder from '@/components/PacketFilterBuilder'
import MultiInterfaceMonitor from '@/components/MultiInterfaceMonitor'

export default function AdvancedFeaturesPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => router.push('/')}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-400" />
              </button>
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Shield className="h-8 w-8 text-blue-500" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Advanced Features</h1>
                <p className="text-sm text-gray-400">Threat Intelligence, Reports, Filters & Multi-Interface Monitoring</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Feature Grid */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Threat Intelligence */}
          <ThreatIntelligence />

          {/* Report Exporter */}
          <ReportExporter />

          {/* Packet Filter Builder */}
          <PacketFilterBuilder />

          {/* Multi-Interface Monitor */}
          <MultiInterfaceMonitor />
        </div>

        {/* Feature Documentation */}
        <div className="mt-8 bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Quick Start Guide</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-300">
            <div>
              <h4 className="font-semibold text-blue-400 mb-2">Threat Intelligence</h4>
              <p className="text-gray-400 mb-2">Enrich detections with IP reputation data from AbuseIPDB and VirusTotal.</p>
              <div className="bg-gray-800/50 rounded p-2 font-mono text-xs text-gray-400">
                # Edit config.yaml<br />
                threat_intel:<br />
                &nbsp;&nbsp;enabled: true<br />
                &nbsp;&nbsp;abuseipdb:<br />
                &nbsp;&nbsp;&nbsp;&nbsp;api_key: "your-key"
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-blue-400 mb-2">Report Export</h4>
              <p className="text-gray-400 mb-2">Generate PDF or CSV reports with detection statistics and visualizations.</p>
              <div className="bg-gray-800/50 rounded p-2 font-mono text-xs text-gray-400">
                # Install reportlab<br />
                pip install reportlab<br />
                <br />
                # API will be available at<br />
                /api/reports/generate
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-blue-400 mb-2">Packet Filtering</h4>
              <p className="text-gray-400 mb-2">Use BPF-style filters to focus on specific traffic patterns.</p>
              <div className="bg-gray-800/50 rounded p-2 font-mono text-xs text-gray-400">
                python main.py --mode detect \<br />
                &nbsp;&nbsp;--interface wlo1 \<br />
                &nbsp;&nbsp;--packet-filter "tcp port 80"
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-blue-400 mb-2">Multi-Interface</h4>
              <p className="text-gray-400 mb-2">Monitor multiple network interfaces simultaneously with aggregated statistics.</p>
              <div className="bg-gray-800/50 rounded p-2 font-mono text-xs text-gray-400">
                python main.py --mode detect \<br />
                &nbsp;&nbsp;--interfaces "wlo1,enp0s25" \<br />
                &nbsp;&nbsp;--backend pyshark
              </div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-500/5 border border-blue-500/20 rounded-lg">
            <p className="text-sm text-blue-400">
              📖 For complete documentation, see <code className="px-2 py-0.5 bg-gray-800 rounded">ADVANCED_FEATURES.md</code> in the project root.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
