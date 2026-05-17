'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { isAuthenticated } from '@/lib/auth'
import { register } from '@/lib/auth'
import { AlertCircle, CheckCircle } from 'lucide-react'

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    phoneNumber: '',
    ageGroup: '',
    guardianName: '',
    guardianEmail: '',
    termsAccepted: false,
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (isAuthenticated()) {
      router.push('/dashboard')
    }
  }, [router])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleAgeGroupChange = (value: string) => {
    setFormData(prev => ({
      ...prev,
      ageGroup: value
    }))
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!formData.fullName || !formData.email || !formData.password || !formData.ageGroup) {
      setError('Please fill in all required fields')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    if (!formData.termsAccepted) {
      setError('You must accept the terms and conditions')
      return
    }

    if (formData.ageGroup === 'under-16' && (!formData.guardianName || !formData.guardianEmail)) {
      setError('Guardian information is required for users under 16')
      return
    }

    setIsLoading(true)

    try {
      const result = await register({
        full_name: formData.fullName,
        email: formData.email,
        password: formData.password,
        phone_number: formData.phoneNumber || null,
      })

      if (result.success) {
        setSuccess('Account created successfully! Redirecting to dashboard...')
        setTimeout(() => {
          router.push('/dashboard')
        }, 1500)
      } else {
        setError(result.message)
      }
    } catch (err) {
      setError('An error occurred during registration. Please try again.')
    }

    setIsLoading(false)
  }

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <Card>
            <CardHeader>
              <CardTitle>Create TrustLine Account</CardTitle>
              <CardDescription>
                Join our community and report incidents safely and securely
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleRegister} className="space-y-6">
                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="w-4 h-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                {success && (
                  <Alert className="bg-green-50 border-green-200">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    <AlertDescription className="text-green-800">{success}</AlertDescription>
                  </Alert>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name *</Label>
                    <Input
                      id="fullName"
                      name="fullName"
                      placeholder="Your full name"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="your@email.com"
                      value={formData.email}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">Password *</Label>
                    <Input
                      id="password"
                      name="password"
                      type="password"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm Password *</Label>
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type="password"
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      disabled={isLoading}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="ageGroup">Age Group *</Label>
                  <Select value={formData.ageGroup} onValueChange={handleAgeGroupChange} disabled={isLoading}>
                    <SelectTrigger id="ageGroup">
                      <SelectValue placeholder="Select your age group" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="16+">16 or older</SelectItem>
                      <SelectItem value="under-16">Under 16</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.ageGroup === 'under-16' && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-4">
                    <p className="text-sm text-amber-900">
                      Since you are under 16, we need your guardian's information to proceed.
                    </p>
                    <div className="space-y-2">
                      <Label htmlFor="guardianName">Guardian Name *</Label>
                      <Input
                        id="guardianName"
                        name="guardianName"
                        placeholder="Guardian's full name"
                        value={formData.guardianName}
                        onChange={handleInputChange}
                        disabled={isLoading}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="guardianEmail">Guardian Email *</Label>
                      <Input
                        id="guardianEmail"
                        name="guardianEmail"
                        type="email"
                        placeholder="guardian@email.com"
                        value={formData.guardianEmail}
                        onChange={handleInputChange}
                        disabled={isLoading}
                      />
                    </div>
                  </div>
                )}

                <div className="flex items-start gap-3">
                  <Checkbox
                    id="terms"
                    name="termsAccepted"
                    checked={formData.termsAccepted}
                    onCheckedChange={(checked) => 
                      setFormData(prev => ({ ...prev, termsAccepted: checked as boolean }))
                    }
                    disabled={isLoading}
                  />
                  <Label htmlFor="terms" className="text-sm cursor-pointer font-normal">
                    I agree to TrustLine's terms of service and privacy policy. I understand my report may be shared with appropriate authorities. *
                  </Label>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-cyan-600 hover:bg-cyan-700" 
                  disabled={isLoading}
                >
                  {isLoading ? 'Creating Account...' : 'Create Account'}
                </Button>

                <div className="text-center text-sm">
                  <p className="text-slate-600">
                    Already have an account?{' '}
                    <Link href="/login" className="text-cyan-600 hover:text-cyan-700 font-medium">
                      Login here
                    </Link>
                  </p>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
      <Footer />
    </>
  )
}
