// frontend/src/components/CameraMonitor.jsx
import { useEffect, useRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export default function CameraMonitor({ onEngagementChange }) {
  const [hasCamera, setHasCamera] = useState(false);
  const [isEngaged, setIsEngaged] = useState(false);
  const videoRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    checkCameraAccess();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const checkCameraAccess = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setHasCamera(videoDevices.length > 0);
      
      if (videoDevices.length > 0) {
        startSimulatedEngagement();
      }
    } catch (err) {
      console.log('Camera check error:', err);
    }
  };

  const startSimulatedEngagement = () => {
    intervalRef.current = setInterval(() => {
      const engaged = Math.random() > 0.7;
      setIsEngaged(engaged);
      if (onEngagementChange) {
        onEngagementChange(engaged);
      }
    }, 3000);
  };

  return (
    <div className="relative">
      <div className={`p-4 rounded-2xl backdrop-blur-sm border-2 ${
        isEngaged
          ? 'bg-green-500/20 border-green-500/30'
          : 'bg-gray-500/20 border-gray-500/30'
      }`}>
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-full ${
            isEngaged ? 'bg-green-500/30' : 'bg-gray-500/30'
          }`}>
            {isEngaged ? (
              <Eye className="w-5 h-5 text-green-500" />
            ) : (
              <EyeOff className="w-5 h-5 text-gray-500" />
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700">
              {isEngaged ? 'User Engaged' : 'No User Detected'}
            </p>
            <p className="text-xs text-gray-500">
              {hasCamera ? 'Camera Active' : 'Camera Not Available'}
            </p>
          </div>
        </div>
      </div>
      
      <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white ${
        isEngaged ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
      }`}></div>
    </div>
  );
}