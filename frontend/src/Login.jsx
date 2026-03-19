import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { loginUser, googleLoginAPI, registerUser } from './api';
import './Login.css';

function Login({ onLogin }) {
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLoginMode) {
        const { success } = await loginUser(email, password);
        if (success) {
          onLogin(true);
          navigate('/');
        } else {
          setError('Invalid email or password.');
        }
      } else {
        await registerUser(email, password, fullName);
        // Automatically log in after successful registration
        const { success } = await loginUser(email, password);
        if (success) {
          onLogin(true);
          navigate('/');
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check your credentials or backend server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h2>{isLoginMode ? 'Welcome Back' : 'Create Account'}</h2>
          <p>{isLoginMode ? 'Sign in to PaperLens' : 'Join PaperLens today'}</p>
        </div>
        <form className="login-form" onSubmit={handleSubmit}>
          {!isLoginMode && (
            <div className="input-group">
              <label htmlFor="fullName">Full Name</label>
              <input 
                id="fullName"
                type="text" 
                value={fullName} 
                onChange={(e) => setFullName(e.target.value)} 
                placeholder="e.g. John Doe"
                required={!isLoginMode} 
              />
            </div>
          )}
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <input 
              id="email"
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              placeholder="e.g. admin@example.com"
              required 
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input 
              id="password"
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="••••••••"
              required 
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (isLoginMode ? 'Signing in...' : 'Creating account...') : (isLoginMode ? 'Sign In' : 'Sign Up')}
          </button>
        </form>

        <div className="toggle-mode">
          <p onClick={() => { setIsLoginMode(!isLoginMode); setError(''); }}>
            {isLoginMode ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </p>
        </div>

        <div style={{ margin: '1.5rem 0', display: 'flex', alignItems: 'center', textAlign: 'center', color: '#999' }}>
            <div style={{ flex: 1, borderBottom: '1px solid #ddd' }}></div>
            <span style={{ padding: '0 10px', fontSize: '0.875rem' }}>OR</span>
            <div style={{ flex: 1, borderBottom: '1px solid #ddd' }}></div>
        </div>

        <div className="google-auth-wrapper" style={{ display: 'flex', justifyContent: 'center' }}>
          <GoogleLogin
            onSuccess={async (credentialResponse) => {
              try {
                const res = await googleLoginAPI(credentialResponse.credential);
                if (res.success) {
                  onLogin(true);
                  navigate('/');
                }
              } catch (err) {
                setError('Google Login failed. Please check backend configuration.');
              }
            }}
            onError={() => {
              setError('Google Login window closed or failed.');
            }}
            theme="filled_blue"
            shape="rectangular"
            text={isLoginMode ? "signin_with" : "signup_with"}
          />
        </div>

        {error && <div className="error-msg">{error}</div>}
      </div>
    </div>
  );
}

export default Login;
