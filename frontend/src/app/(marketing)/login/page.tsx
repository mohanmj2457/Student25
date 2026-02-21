import { AuthForm } from '@/components/auth/AuthForm';
import { ShaderAnimation } from '@/components/gpa/ShaderAnimation';

export default function LoginPage() {
  return (
    <div className="relative w-full h-screen flex items-center justify-center">
       <div className="absolute inset-0 z-0">
          <ShaderAnimation />
        </div>
        <div className="relative z-10 w-full px-4">
          <AuthForm />
        </div>
    </div>
  );
}
