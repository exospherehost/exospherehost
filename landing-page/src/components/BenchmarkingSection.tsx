import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";
import { pattanakarn, darkerGrotesque } from "@/lib/fonts"

const costData = [
  { name: 'Jan', Exosphere: 0.12, OtherProviders: 0.25 },
  { name: 'Feb', Exosphere: 0.11, OtherProviders: 0.23 },
  { name: 'Mar', Exosphere: 0.10, OtherProviders: 0.22 },
  { name: 'Apr', Exosphere: 0.09, OtherProviders: 0.21 },
  { name: 'May', Exosphere: 0.08, OtherProviders: 0.20 },
  { name: 'Jun', Exosphere: 0.08, OtherProviders: 0.19 },
];

const reliabilityData = [
  { name: 'Jan', Uptime: 99.8, Incidents: 2 },
  { name: 'Feb', Uptime: 99.9, Incidents: 1 },
  { name: 'Mar', Uptime: 99.95, Incidents: 1 },
  { name: 'Apr', Uptime: 99.97, Incidents: 0 },
  { name: 'May', Uptime: 99.99, Incidents: 0 },
  { name: 'Jun', Uptime: 99.99, Incidents: 0 },
];

export default function BenchmarkingSection() {
  return (
    <div className="w-full flex flex-col md:flex-row gap-12 justify-center items-center py-16 px-4 mx-auto bg-[var(--color-1)]">
      {/* Decreased Cost Section */}
      <div className="flex-1 bg-[var(--color-1)]/90 rounded-2xl backdrop-blur-lg p-10 flex flex-col items-center">
        <h2 className={`${pattanakarn.className} text-3xl text-white mb-2`}>batch and save on agents</h2>
        <p className={`${darkerGrotesque.className} text-[#B3D6FF] mb-6 text-center`}>Save up to 60% thanks to batching optimizations</p>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={costData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="rgba(255,255,255,0.3)" />
            <XAxis
              dataKey="name"
              stroke="rgba(255,255,255,0.7)"
              tickLine={false}
              axisLine={{stroke:'rgba(255,255,255,0.3)'}}
              style={{ fontFamily: darkerGrotesque.className, fontSize: 16 }}
            />
            <YAxis
              stroke="rgba(255,255,255,0.7)"
              domain={[0, 0.3]}
              tickFormatter={v => `$${v.toFixed(2)}`}
              tickLine={false}
              axisLine={{stroke:'rgba(255,255,255,0.3)'}}
              style={{ fontFamily: darkerGrotesque.className, fontSize: 16 }}
            />
            <Tooltip
              contentStyle={{
                background: '#031035',
                border: 'none',
                color: '#fff',
                borderRadius: 10,
                boxShadow: '0 2px 12px #0004',
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
              itemStyle={{
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
              labelStyle={{
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
            />
            <Legend
              iconType="plainline"
              wrapperStyle={{
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
            />
            <Line type="monotone" dataKey="Exosphere" stroke="#7FD6FF" strokeWidth={3} dot={{ r: 4, fill: '#031035', stroke: '#fff', strokeWidth: 1 }} activeDot={{ r: 7, fill: '#031035', stroke: '#fff', strokeWidth: 2 }} />
            <Line type="monotone" dataKey="OtherProviders" stroke="#FF5D73" strokeWidth={3} dot={{ r: 4, fill: '#FF5D73', stroke: '#fff', strokeWidth: 1 }} activeDot={{ r: 7, fill: '#FF5D73', stroke: '#fff', strokeWidth: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {/* Reliability Section */}
      <div className="flex-1 bg-[var(--color-1)]/90 rounded-2xl backdrop-blur-lg p-10 flex flex-col items-center">
        <h2 className={`${pattanakarn.className} text-3xl text-white mb-2`}>reliability first, always</h2>
        <p className={`${darkerGrotesque.className} text-[#B3D6FF] mb-6 text-center`}>For workloads that <b>need</b> to be running</p>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={reliabilityData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="rgba(255,255,255,0.3)" />
            <XAxis
              dataKey="name"
              stroke="rgba(255,255,255,0.7)"
              tickLine={false}
              axisLine={{stroke:'rgba(255,255,255,0.3)'}}
              style={{ fontFamily: darkerGrotesque.className, fontSize: 16 }}
            />
            <YAxis
              yAxisId="left"
              stroke="rgba(255,255,255,0.7)"
              domain={[99.7, 100]}
              tickFormatter={v => `${v}%`}
              tickLine={false}
              axisLine={{stroke:'rgba(255,255,255,0.3)'}}
              style={{ fontFamily: darkerGrotesque.className, fontSize: 16 }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="rgba(255,255,255,0.7)"
              domain={[0, 3]}
              tickLine={false}
              axisLine={{stroke:'rgba(255,255,255,0.3)'}}
              style={{ fontFamily: darkerGrotesque.className, fontSize: 16 }}
            />
            <Tooltip
              contentStyle={{
                background: '#031035',
                border: 'none',
                color: '#fff',
                borderRadius: 10,
                boxShadow: '0 2px 12px #0004',
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
              itemStyle={{
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
              labelStyle={{
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
            />
            <Legend
              iconType="rect"
              wrapperStyle={{
                fontFamily: darkerGrotesque.className,
                fontSize: 16,
              }}
            />
            <Bar yAxisId="left" dataKey="Uptime" fill="#7FD6FF" radius={[2, 2, 0, 0]} barSize={22} />
            <Bar yAxisId="right" dataKey="Incidents" fill="#FF5D73" radius={[2, 2, 0, 0]} barSize={14} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
} 