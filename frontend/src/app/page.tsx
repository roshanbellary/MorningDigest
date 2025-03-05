'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"

interface DigestItem {
  content: Array<{ subject: string; content: string }>;
  email_count: number;
  sources: Array<{ subject: string; sender: string }>;
}

interface DigestResponse {
  message: string;
  date: string;
  total_emails: number;
  industries: string[];
  digests: Record<string, DigestItem>;
}

export default function Home() {
  const [date, setDate] = useState('')
  const [loading, setLoading] = useState(false)
  const [digests, setDigests] = useState<DigestResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setDigests(null)

    try {
      setLoading(true)
      const response = await fetch('http://127.0.0.1:5000/api/process-emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          date,
          industries: ['Technology', 'Finance', 'Healthcare', 'Education', 'Entertainment']
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch digests')
      }

      const data = await response.json()
      if (data.error) {
        throw new Error(data.error)
      }
      console.log(data);
      setDigests(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container mx-auto p-4 max-w-5xl">
      <div className="space-y-8">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Morning Digest</h1>
          <p className="text-gray-500">Get a summary of your emails by industry</p>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-4 items-end">
          <div className="flex-1 space-y-2">
            <label htmlFor="date" className="text-sm font-medium">
              Select Date
            </label>
            <Input
              id="date"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </div>
          <Button type="submit" disabled={loading}>
            {loading ? <Spinner className="mr-2" /> : null}
            Generate Digest
          </Button>
        </form>

        {error && (
          <div className="p-4 text-red-700 bg-red-50 rounded-md">
            {error}
          </div>
        )}

        {digests && !loading && (
          <div className="grid grid-cols-1 gap-6">
            {Object.entries(digests.digests).map(([industry, data]) => (
              <Card key={industry} className="mb-4 overflow-hidden">
                <CardHeader className="bg-gray-50">
                  <CardTitle className="text-xl">{industry}</CardTitle>
                  <CardDescription>
                    {data.email_count} email{data.email_count !== 1 ? 's' : ''} processed
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-6">
                    {data.content.map((item, index) => (
                      <div key={index} className="pb-4 last:pb-0 last:border-0">
                        <h3 className="text-lg font-bold text-gray-900 mb-2">
                          {item.subject}
                        </h3>
                        <p className="text-gray-700 leading-relaxed">
                          {item.content}
                        </p>
                      </div>
                    ))}
                    
                    <div className="mt-6 pt-4 border-t border-gray-200">
                      <h4 className="font-semibold text-gray-900 mb-3">Sources:</h4>
                      <ul className="list-disc pl-5 space-y-1.5">
                        {data.sources.map((source, index) => (
                          <li key={index} className="text-sm text-gray-600">
                            <span className="font-medium">{source.subject}</span>
                            <span className="text-gray-400"> - {source.sender}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
