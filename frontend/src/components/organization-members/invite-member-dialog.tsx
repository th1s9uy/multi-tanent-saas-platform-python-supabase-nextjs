'use client';

import React, { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, Mail } from 'lucide-react';
import { organizationService } from '@/services/organization-service';

interface InviteMemberDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export function InviteMemberDialog({ open, onOpenChange, onSuccess }: InviteMemberDialogProps) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const searchParams = useSearchParams();
  const orgId = searchParams.get('org_id');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !orgId) {
      toast.error('Please provide a valid email address.');
      return;
    }

    setLoading(true);

    try {
      const invitation = await organizationService.inviteMember(orgId, email);

      if (invitation) {
        // Show different messages based on invitation type
        if (invitation.status === 'accepted') {
          // User was added directly to the organization
          toast.success(`${email} has been added to the organization!`);
        } else {
          // New invitation was sent
          toast.success(`Invitation sent to ${email}`);
        }

        setEmail('');
        onOpenChange(false);
        onSuccess?.();
      }

    } catch (error) {
      console.log('Invitation error:', error);

      // Parse error response to get error code
      let errorCode = '';
      let errorMessage = '';

      if (error instanceof Error && 'message' in error) {
        try {
          // Try to parse as JSON if it's a string
          const parsed = typeof error.message === 'string'
            ? JSON.parse(error.message)
            : error.message;

          errorCode = (parsed as { error_code?: string; message?: string }).error_code || '';
          errorMessage = (parsed as { error_code?: string; message?: string }).message || error.message;
        } catch {
          errorMessage = error.message;
        }
      }

      // Show specific message based on error code
      switch (errorCode) {
        case 'USER_ALREADY_MEMBER':
          toast.error(`User with email '${email}' is already a member of this organization.`);
          break;
        case 'INSUFFICIENT_PERMISSIONS':
          toast.error('You do not have permission to invite members to this organization.');
          break;
        case 'VALIDATION_ERROR':
          toast.error(errorMessage || 'Invalid input provided.');
          break;
        default:
          toast.error(errorMessage || 'Failed to send invitation');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <Mail className="h-5 w-5" />
            <span>Invite Member</span>
          </DialogTitle>
          <DialogDescription>
            Send an invitation email to add a new member to your organization. They will receive a link to join after signing up.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="colleague@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
              />
              <p className="text-sm text-muted-foreground">
                We&apos;ll send an invitation email with a link to sign up.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                'Send Invitation'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
