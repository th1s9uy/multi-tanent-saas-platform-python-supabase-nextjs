'use client';

import React, { useState } from 'react';
import { AlertTriangle, Mail, Loader2, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { resendVerificationEmail } from '@/lib/supabase';

interface EmailVerificationBannerProps {
  email: string;
  onClose?: () => void;
}

export function EmailVerificationBanner({ email, onClose }: EmailVerificationBannerProps) {
  const [isResending, setIsResending] = useState(false);
  const [resendStatus, setResendStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleResendEmail = async () => {
    if (!email) {
      setErrorMessage('Email address is required');
      setResendStatus('error');
      return;
    }

    setIsResending(true);
    setResendStatus('idle');
    setErrorMessage('');

    try {
      await resendVerificationEmail(email);
      setResendStatus('success');
    } catch (error) {
      console.error('Error resending verification email:', error);
      setResendStatus('error');
      
      // Handle specific Supabase error cases
      if (error && typeof error === 'object' && 'message' in error) {
        const errorMsg = error.message as string;
        if (errorMsg.toLowerCase().includes('email rate limit')) {
          setErrorMessage('Please wait a few minutes before requesting another verification email.');
        } else if (errorMsg.toLowerCase().includes('email not found')) {
          setErrorMessage('We could not find an account with this email address.');
        } else {
          setErrorMessage('Failed to resend verification email. Please try again.');
        }
      } else {
        setErrorMessage('Failed to resend verification email. Please try again.');
      }
    } finally {
      setIsResending(false);
    }
  };

  if (resendStatus === 'success') {
    return (
      <Alert className="mb-6 bg-green-50 border-green-200">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <div>
            <div className="mb-3">
              <strong>Verification email sent!</strong>
              <p className="text-sm mt-1">
                We&apos;ve sent a new verification email to <strong>{email}</strong>.
                Please check your inbox and click the verification link.
              </p>
            </div>
            {onClose && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-green-600 hover:text-green-800"
              >
                Dismiss
              </Button>
            )}
          </div>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Alert className="mb-6 bg-amber-50 border-amber-200">
      <AlertTriangle className="h-4 w-4 text-amber-600" />
      <AlertDescription className="text-amber-800">
        <div>
          <div className="mb-3">
            <strong>Email verification required</strong>
            <p className="text-sm mt-1">
              Please verify your email address <strong>{email}</strong> to continue using the application.
              Click the verification link sent to your email.
            </p>

            {errorMessage && (
              <p className="text-sm mt-2 text-red-600 bg-red-100 p-2 rounded">
                {errorMessage}
              </p>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <Button
              onClick={handleResendEmail}
              disabled={isResending || !email}
              size="sm"
              variant="outline"
              className="bg-white border-amber-300 text-amber-700 hover:bg-amber-50"
            >
              {isResending ? (
                <>
                  <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Mail className="mr-2 h-3 w-3" />
                  Resend Email
                </>
              )}
            </Button>

            {onClose && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                className="text-amber-600 hover:text-amber-800"
              >
                Dismiss
              </Button>
            )}
          </div>
        </div>
      </AlertDescription>
    </Alert>
  );
}
