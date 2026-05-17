'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { isAuthenticated } from '@/lib/auth'
import apiFetch from '@/lib/api'
import { MessageCircle, Send, Moon, Sun, AlertCircle, CheckCircle, Loader, Bot, User } from 'lucide-react'

interface ChatMessage {
  id: number | string
  sender: 'user' | 'bot'
  content: string
  created_at: string
}

interface SessionState {
  mode: string
  incident_type: string | null
  complaint_submitted: boolean
  tracking_id: string | null
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sessionState, setSessionState] = useState<SessionState | null>(null)
  const [isInitializing, setIsInitializing] = useState(true)
  const [isGuest, setIsGuest] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  // Initialize chat session
  useEffect(() => {
    setIsGuest(!isAuthenticated())
    initSession()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const initSession = async () => {
    try {
      setIsInitializing(true)
      const data = await apiFetch<{ session_id: string }>('/chatbot/sessions', { method: 'POST' })
      setSessionId(data.session_id)

      // Load any existing messages
      const history = await apiFetch<ChatMessage[]>(`/chatbot/sessions/${data.session_id}/messages`)
      if (history && history.length > 0) {
        setMessages(history)
      }

      // Load session state
      const state = await apiFetch<SessionState>(`/chatbot/sessions/${data.session_id}/state`)
      setSessionState(state)
    } catch (err) {
      console.error('Failed to initialize chat session:', err)
    } finally {
      setIsInitializing(false)
    }
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || !sessionId || isLoading) return

    const userText = inputText.trim()
    setInputText('')
    setIsLoading(true)

    // Optimistically add user message
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      sender: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMsg])

    try {
      const response = await apiFetch<{
        user_message: ChatMessage
        bot_message: ChatMessage
        mode: string
        incident_type: string | null
        complaint_submitted: boolean
        tracking_id: string | null
      }>(`/chatbot/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content: userText }),
      })

      // Replace temp message with real ones
      setMessages(prev => {
        const filtered = prev.filter(m => m.id !== tempUserMsg.id)
        return [...filtered, response.user_message, response.bot_message]
      })

      // Update session state
      setSessionState({
        mode: response.mode,
        incident_type: response.incident_type,
        complaint_submitted: response.complaint_submitted,
        tracking_id: response.tracking_id,
      })
    } catch (err) {
      console.error('Failed to send message:', err)
      // Remove optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id))
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const getModeLabel = (mode: string): string => {
    switch (mode) {
      case 'guided_intake': return 'Filing your complaint...'
      case 'vulnerable_support': return 'Support mode'
      case 'hard_crisis': return 'Crisis support'
      case 'post_complaint': return 'Complaint filed'
      default: return ''
    }
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 h-[calc(100vh-200px)] flex flex-col">
          {/* Header */}
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-2">
                <MessageCircle className="w-8 h-8 text-cyan-600" />
                Mithuru - TrustLine Support
              </h1>
              <div className="flex items-center gap-3 mt-1">
                <p className="text-slate-600 text-sm">24/7 AI Support • All conversations are encrypted</p>
                {sessionState && sessionState.mode !== 'support' && (
                  <Badge variant="secondary" className="text-xs">
                    {getModeLabel(sessionState.mode)}
                  </Badge>
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="h-9 w-9"
            >
              {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
          </div>

          {/* Success Banner */}
          {sessionState?.complaint_submitted && sessionState.tracking_id && (
            <Card className="mb-4 bg-green-50 border-green-200">
              <CardContent className="pt-6">
                <div className="flex gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
                  <div>
                    <p className="font-semibold text-green-900">Complaint Filed Successfully</p>
                    <p className="text-sm text-green-800 mt-1">
                      Tracking ID: <strong>{sessionState.tracking_id}</strong>
                    </p>
                    <p className="text-sm text-green-700 mt-2">Save this ID to track your complaint.</p>
                    {!isGuest && (
                      <Button asChild size="sm" className="mt-3 bg-green-600 hover:bg-green-700">
                        <Link href="/dashboard">View Dashboard</Link>
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Chat Container */}
          <Card className={`flex-1 flex flex-col mb-4 overflow-hidden ${isDarkMode ? 'bg-slate-800 border-slate-700' : ''}`}>
            {/* Messages */}
            <CardContent className={`flex-1 overflow-y-auto p-6 space-y-4 ${isDarkMode ? 'bg-slate-800' : ''}`}>
              {isInitializing ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Loader className="w-8 h-8 animate-spin text-cyan-600 mx-auto mb-3" />
                    <p className={`text-sm ${isDarkMode ? 'text-slate-400' : 'text-slate-600'}`}>
                      Connecting to Mithuru...
                    </p>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`flex gap-2 max-w-xs lg:max-w-md xl:max-w-lg ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                          msg.sender === 'user' ? 'bg-cyan-600' : 'bg-slate-600'
                        }`}>
                          {msg.sender === 'user' ? (
                            <User className="w-4 h-4 text-white" />
                          ) : (
                            <Bot className="w-4 h-4 text-white" />
                          )}
                        </div>
                        <div
                          className={`px-4 py-3 rounded-lg ${
                            msg.sender === 'user'
                              ? 'bg-cyan-600 text-white rounded-br-none'
                              : isDarkMode
                              ? 'bg-slate-700 text-white rounded-bl-none'
                              : 'bg-slate-100 text-slate-900 rounded-bl-none'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                          <p className={`text-xs mt-1 ${msg.sender === 'user' ? 'text-cyan-100' : isDarkMode ? 'text-slate-400' : 'text-slate-500'}`}>
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="flex gap-2">
                        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className={`px-4 py-3 rounded-lg rounded-bl-none ${isDarkMode ? 'bg-slate-700' : 'bg-slate-100'}`}>
                          <div className="flex gap-1">
                            <span className={`w-2 h-2 rounded-full animate-bounce ${isDarkMode ? 'bg-slate-400' : 'bg-slate-400'}`} style={{ animationDelay: '0ms' }}></span>
                            <span className={`w-2 h-2 rounded-full animate-bounce ${isDarkMode ? 'bg-slate-400' : 'bg-slate-400'}`} style={{ animationDelay: '150ms' }}></span>
                            <span className={`w-2 h-2 rounded-full animate-bounce ${isDarkMode ? 'bg-slate-400' : 'bg-slate-400'}`} style={{ animationDelay: '300ms' }}></span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </CardContent>

            {/* Input Area */}
            <form
              onSubmit={handleSendMessage}
              className={`border-t ${isDarkMode ? 'border-slate-700 bg-slate-750' : 'border-slate-200'} p-4 flex gap-3`}
            >
              <Input
                ref={inputRef}
                placeholder="Type your message..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isLoading || isInitializing}
                className={`flex-1 ${isDarkMode ? 'bg-slate-700 border-slate-600 text-white' : ''}`}
              />
              <Button
                type="submit"
                disabled={isLoading || isInitializing || !inputText.trim()}
                className="bg-cyan-600 hover:bg-cyan-700"
              >
                {isLoading ? <Loader className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </form>
          </Card>

          {/* Footer Info */}
          <Alert className="bg-cyan-50 border-cyan-200">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="text-cyan-900">
              All conversations are confidential. You can track your case status by logging in to your dashboard or using your Tracking ID.
            </AlertDescription>
          </Alert>
        </div>
      </main>
      <Footer />
    </>
  )
}
