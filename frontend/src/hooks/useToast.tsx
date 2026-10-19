import { createContext, useContext, useState, useCallback, useRef, type ReactNode } from "react";
import { motion } from "framer-motion";
import { CheckCircle, XCircle, AlertCircle, Info, X } from "lucide-react";

interface Toast {
  id: number;
  type: "success" | "error" | "warning" | "info";
  message: string;
}

interface ToastContextType {
  toasts: Toast[];
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  showWarning: (message: string) => void;
  showInfo: (message: string) => void;
  dismiss: (id: number) => void;
}

const ToastContext = createContext<ToastContextType | null>(null);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const idCounter = useRef(0);

  const showToast = useCallback((type: Toast["type"], message: string) => {
    const id = ++idCounter.current;
    setToasts(prev => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  }, []);

  const showSuccess = useCallback((message: string) => showToast("success", message), [showToast]);
  const showError = useCallback((message: string) => showToast("error", message), [showToast]);
  const showWarning = useCallback((message: string) => showToast("warning", message), [showToast]);
  const showInfo = useCallback((message: string) => showToast("info", message), [showToast]);

  const dismiss = useCallback((id: number) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, showSuccess, showError, showWarning, showInfo, dismiss }}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

function ToastContainer({ toasts, onDismiss }: { toasts: Toast[]; onDismiss: (id: number) => void }) {
  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <motion.div
          key={toast.id}
          className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg min-w-[300px] max-w-md ${
            toast.type === "success" ? "bg-green-600 text-white" :
            toast.type === "error" ? "bg-red-600 text-white" :
            toast.type === "warning" ? "bg-yellow-600 text-white" :
            "bg-blue-600 text-white"
          }`}
          initial={{ opacity: 0, x: 100, scale: 0.95 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 100, scale: 0.95 }}
          transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
        >
          {toast.type === "success" && <CheckCircle className="w-5 h-5 flex-shrink-0" />}
          {toast.type === "error" && <XCircle className="w-5 h-5 flex-shrink-0" />}
          {toast.type === "warning" && <AlertCircle className="w-5 h-5 flex-shrink-0" />}
          {toast.type === "info" && <Info className="w-5 h-5 flex-shrink-0" />}
          <p className="text-sm font-medium flex-1">{toast.message}</p>
          <button
            onClick={() => onDismiss(toast.id)}
            className="p-1 hover:bg-white/20 rounded-lg transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      ))}
    </div>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}