'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { LogIn, UserPlus } from 'lucide-react';

export function AuthForm() {
  const [isLogin, setIsLogin] = useState(true);
  const router = useRouter();
  const emailRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Extract USN from email (e.g. 1RN22CS001@student.edu -> 1RN22CS001)
    const email = emailRef.current?.value || '';
    const usn = email.split('@')[0].toUpperCase();

    console.log('Auth form submitted for:', isLogin ? 'Login' : 'Sign Up');

    // Redirect to the dashboard page, passing the USN as state
    if (usn) {
      router.push(`/dashboard?usn=${encodeURIComponent(usn)}`);
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto glass-card">
      <CardHeader className="text-center">
        <CardTitle className="text-3xl font-headline">
          {isLogin ? 'Welcome Back!' : 'Create an Account'}
        </CardTitle>
        <CardDescription>
          {isLogin
            ? "Sign in to access your dashboard."
            : 'Get started with Padhloo today.'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="m@example.com" required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" required />
          </div>
          {!isLogin && (
            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm Password</Label>
              <Input id="confirm-password" type="password" required />
            </div>
          )}
          <Button type="submit" className="w-full font-bold text-lg py-6 bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-300 hover:glow-primary">
            {isLogin ? (
              <>
                <LogIn className="mr-2 h-5 w-5" /> Sign In
              </>
            ) : (
              <>
                <UserPlus className="mr-2 h-5 w-5" /> Sign Up
              </>
            )}
          </Button>
        </form>
      </CardContent>
      <CardFooter className="flex justify-center">
        <Button variant="link" onClick={() => setIsLogin(!isLogin)}>
          {isLogin
            ? "Don't have an account? Sign Up"
            : 'Already have an account? Sign In'}
        </Button>
      </CardFooter>
    </Card>
  );
}
