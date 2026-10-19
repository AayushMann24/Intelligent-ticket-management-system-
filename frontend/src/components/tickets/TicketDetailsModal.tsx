import { useEffect, useState, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import type { Ticket, TimelineItem, TimelineItemType, WorkflowActions } from "../../types/ticket";
import type { Technician } from "../../services/userService";

import {
  X, Ticket as TicketIcon, Bot, User, Calendar, Brain,
  Play, Pause, CheckCircle, XCircle, ArrowRight, AlertTriangle,
  Clock, History, MessageSquare, Paperclip, UserPlus, UserMinus,
  Loader2
} from "lucide-react";
import { useReducedMotion } from "../../hooks/useReducedMotion";
import { useAuth } from "../../context/useAuth";
import useTickets from "../../hooks/useTickets";
import { useToast } from "../../hooks/useToast";
import TicketAttachmentsPanel from "./TicketAttachmentsPanel";

interface TicketDetailsModalProps {
  open: boolean;
  ticket: Ticket | null;
  onClose: () => void;
  onRefresh?: () => Promise<void>;
}

type ActiveTab = "details" | "timeline";

interface ActionDialogState {
  type: "assign" | "reassign" | "unassign" | "startWork" | "markPending" | "resolve" | "reopen" | "close" | "escalate" | null;
  isOpen: boolean;
  loading: boolean;
  error: string | null;
}

export default function TicketDetailsModal({ open, ticket, onClose, onRefresh }: TicketDetailsModalProps) {
  const reducedMotion = useReducedMotion();
  const { user } = useAuth();
  const { 
    fetchWorkflowActions, 
    assignTechnician, 
    reassignTechnician, 
    unassignTechnician, 
    startWorkOnTicket, 
    markTicketPending, 
    resolveTicketAction, 
    reopenTicketAction, 
    closeTicketAction, 
    escalateTicketAction,
    fetchTechnicians 
  } = useTickets();
  const { showSuccess, showError } = useToast();

  const [workflowActions, setWorkflowActions] = useState<WorkflowActions | null>(null);
  const [technicians, setTechnicians] = useState<Technician[]>([]);
  const [activeTab, setActiveTab] = useState<ActiveTab>("details");
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [actionDialog, setActionDialog] = useState<ActionDialogState>({
    type: null,
    isOpen: false,
    loading: false,
    error: null,
  });
  const [formData, setFormData] = useState<{
    assignedTo: number | null;
    reason: string;
    resolutionSummary: string;
    escalatedTo: number | null;
    escalationReason: string;
  }>({
    assignedTo: null,
    reason: "",
    resolutionSummary: "",
    escalatedTo: null,
    escalationReason: "",
  });
  const ticketIdRef = useRef<number | null>(null);

  // Load workflow actions and technicians when ticket changes
  useEffect(() => {
    if (!open || !ticket) {
      setWorkflowActions(null);
      setTechnicians([]);
      return;
    }

    ticketIdRef.current = ticket.id;

    const loadData = async () => {
      try {
        const [actions, techs] = await Promise.all([
          fetchWorkflowActions(ticket.id),
          fetchTechnicians(),
        ]);
        if (ticketIdRef.current === ticket.id) {
          setWorkflowActions(actions);
          setTechnicians(techs);
        }
      } catch (error) {
        console.error("Failed to load workflow data:", error);
      }
    };

    loadData();
  }, [open, ticket, fetchWorkflowActions, fetchTechnicians]);

  // Load timeline when tab is activated
  useEffect(() => {
    if (!open || !ticket || activeTab !== "timeline") return;

    const loadTimeline = async () => {
      setTimelineLoading(true);
      try {
        // We'll fetch timeline via the ticket service directly
        const response = await fetch(`/tickets/${ticket.id}/timeline?page_size=100`, {
          headers: { "Authorization": `Bearer ${localStorage.getItem("access_token")}` }
        });
        if (response.ok) {
          const data = await response.json();
          if (ticketIdRef.current === ticket.id) {
            setTimeline(data.items || []);
          }
        }
      } catch (error) {
        console.error("Failed to load timeline:", error);
      } finally {
        if (ticketIdRef.current === ticket.id) {
          setTimelineLoading(false);
        }
      }
    };

    loadTimeline();
  }, [open, ticket, activeTab]);

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (actionDialog.isOpen) {
          closeActionDialog();
        } else {
          onClose();
        }
      }
    };
    if (open) {
      window.addEventListener("keydown", handleEscape);
    }
    return () => window.removeEventListener("keydown", handleEscape);
  }, [open, actionDialog.isOpen, onClose]);

  if (!open || !ticket) return null;

  const priorityColor = {
    High: "bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400",
    Medium: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    Low: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
    Critical: "bg-red-200 text-red-800 dark:bg-red-500/30 dark:text-red-300",
  };

  const statusColor = {
    Open: "bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400",
    Assigned: "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400",
    "In Progress": "bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400",
    Pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-500/20 dark:text-yellow-400",
    Resolved: "bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400",
    Closed: "bg-slate-100 text-slate-700 dark:bg-slate-500/20 dark:text-slate-400",
  };

  const modalTransition = reducedMotion
    ? { duration: 0 }
    : { type: "spring" as const, stiffness: 300, damping: 30 };

  const backdropTransition = reducedMotion
    ? { duration: 0 }
    : { duration: 0.15 };

  // Dialog handlers
  const openActionDialog = useCallback((type: ActionDialogState["type"]) => {
    setFormData({ assignedTo: null, reason: "", resolutionSummary: "", escalatedTo: null, escalationReason: "" });
    setActionDialog({ type, isOpen: true, loading: false, error: null });
  }, []);

  const closeActionDialog = useCallback(() => {
    setActionDialog({ type: null, isOpen: false, loading: false, error: null });
    setFormData({ assignedTo: null, reason: "", resolutionSummary: "", escalatedTo: null, escalationReason: "" });
  }, []);

  const handleActionSubmit = async () => {
    if (!ticket || !actionDialog.type || actionDialog.loading) return;

    setActionDialog(prev => ({ ...prev, loading: true, error: null }));

    try {
      let successMessage = "";
      
      switch (actionDialog.type) {
        case "assign":
          if (!formData.assignedTo) throw new Error("Please select a technician");
          await assignTechnician(ticket.id, Number(formData.assignedTo));
          successMessage = "Ticket assigned successfully";
          break;
        case "reassign":
          if (!formData.assignedTo) throw new Error("Please select a technician");
          await reassignTechnician(ticket.id, Number(formData.assignedTo));
          successMessage = "Ticket reassigned successfully";
          break;
        case "unassign":
          await unassignTechnician(ticket.id);
          successMessage = "Ticket unassigned successfully";
          break;
        case "startWork":
          await startWorkOnTicket(ticket.id);
          successMessage = "Work started successfully";
          break;
        case "markPending":
          if (!formData.reason.trim()) throw new Error("Pending reason is required");
          await markTicketPending(ticket.id, formData.reason.trim());
          successMessage = "Ticket marked as pending";
          break;
        case "resolve":
          if (!formData.resolutionSummary.trim()) throw new Error("Resolution summary is required");
          await resolveTicketAction(ticket.id, formData.resolutionSummary.trim());
          successMessage = "Ticket resolved successfully";
          break;
        case "reopen":
          await reopenTicketAction(ticket.id, formData.reason.trim() || undefined);
          successMessage = "Ticket reopened successfully";
          break;
        case "close":
          await closeTicketAction(ticket.id);
          successMessage = "Ticket closed successfully";
          break;
        case "escalate":
          if (!formData.escalatedTo) throw new Error("Please select a user to escalate to");
          if (!formData.escalationReason.trim()) throw new Error("Escalation reason is required");
          await escalateTicketAction(ticket.id, Number(formData.escalatedTo), formData.escalationReason.trim());
          successMessage = "Ticket escalated successfully";
          break;
      }

      showSuccess(successMessage);
      closeActionDialog();
      
      // Refresh ticket data
      if (onRefresh) {
        await onRefresh();
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || error.message || "Operation failed";
      setActionDialog(prev => ({ ...prev, loading: false, error: message }));
      showError(message);
    }
  };

  // Get current user role for permission checks
  const userRole = user?.role || "Employee";

  // Render action buttons based on workflow actions
  const renderActionButtons = () => {
    if (!workflowActions) return null;

    const buttons: React.ReactNode[] = [];

    // Admin actions
    if (workflowActions.can_assign && userRole === "Admin" && !ticket.assigned_to) {
      buttons.push(
        <motion.button
          key="assign"
          onClick={() => openActionDialog("assign")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <UserPlus size={16} /> Assign
        </motion.button>
      );
    }

    if (workflowActions.can_reassign && userRole === "Admin" && ticket.assigned_to) {
      buttons.push(
        <motion.button
          key="reassign"
          onClick={() => openActionDialog("reassign")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <UserPlus size={16} /> Reassign
        </motion.button>
      );
    }

    if (workflowActions.can_unassign && userRole === "Admin" && ticket.assigned_to) {
      buttons.push(
        <motion.button
          key="unassign"
          onClick={() => openActionDialog("unassign")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-600 text-white text-sm font-medium hover:bg-slate-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <UserMinus size={16} /> Unassign
        </motion.button>
      );
    }

    // Assignee/Admin actions
    if (workflowActions.can_start_work && ticket.assigned_to) {
      buttons.push(
        <motion.button
          key="startWork"
          onClick={() => openActionDialog("startWork")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-medium hover:bg-green-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <Play size={16} /> Start Work
        </motion.button>
      );
    }

    if (workflowActions.can_mark_pending && ticket.assigned_to) {
      buttons.push(
        <motion.button
          key="markPending"
          onClick={() => openActionDialog("markPending")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-yellow-600 text-white text-sm font-medium hover:bg-yellow-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <Pause size={16} /> Mark Pending
        </motion.button>
      );
    }

    if (workflowActions.can_resolve && ticket.assigned_to) {
      buttons.push(
        <motion.button
          key="resolve"
          onClick={() => openActionDialog("resolve")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <CheckCircle size={16} /> Resolve
        </motion.button>
      );
    }

    if (workflowActions.can_reopen && (userRole === "Admin" || ticket.created_by === user?.id || ticket.assigned_to === user?.id)) {
      buttons.push(
        <motion.button
          key="reopen"
          onClick={() => openActionDialog("reopen")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-orange-600 text-white text-sm font-medium hover:bg-orange-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <ArrowRight size={16} /> Reopen
        </motion.button>
      );
    }

    if (workflowActions.can_close && userRole !== "Employee") {
      buttons.push(
        <motion.button
          key="close"
          onClick={() => openActionDialog("close")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-600 text-white text-sm font-medium hover:bg-slate-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <XCircle size={16} /> Close
        </motion.button>
      );
    }

    if (workflowActions.can_escalate && (userRole === "Admin" || ticket.assigned_to === user?.id)) {
      buttons.push(
        <motion.button
          key="escalate"
          onClick={() => openActionDialog("escalate")}
          disabled={actionDialog.loading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition-colors disabled:opacity-50"
          whileHover={reducedMotion ? {} : { scale: 1.02 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <AlertTriangle size={16} /> Escalate
        </motion.button>
      );
    }

    if (buttons.length === 0) return null;

    return (
      <motion.div
        className="sticky bottom-0 z-10 mt-8 flex flex-wrap gap-3 border-t border-slate-200 bg-white px-8 py-6 dark:border-slate-800 dark:bg-slate-900"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, delay: 0.3 }}
      >
        <div className="flex flex-wrap gap-3 w-full">
          {buttons}
        </div>
      </motion.div>
    );
  };

  // Render action dialog content
  const renderActionDialog = () => {
    if (!actionDialog.isOpen || !actionDialog.type) return null;

    const dialogs: Record<string, React.ReactNode> = {
      assign: (
        <TechnicianPickerDialog
          title="Assign Ticket"
          description="Select a technician to assign this ticket to"
          technicians={technicians}
          selectedId={formData.assignedTo}
          onSelect={(id) => setFormData(prev => ({ ...prev, assignedTo: id }))}
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          error={actionDialog.error}
        />
      ),
      reassign: (
        <TechnicianPickerDialog
          title="Reassign Ticket"
          description="Select a new technician for this ticket"
          technicians={technicians.filter(t => t.id !== ticket.assigned_to)}
          selectedId={formData.assignedTo}
          onSelect={(id) => setFormData(prev => ({ ...prev, assignedTo: id }))}
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          error={actionDialog.error}
        />
      ),
      unassign: (
        <ConfirmDialog
          title="Unassign Ticket"
          message="Are you sure you want to unassign this ticket? It will be returned to Open status."
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          confirmText="Unassign"
          variant="destructive"
        />
      ),
      startWork: (
        <ConfirmDialog
          title="Start Work"
          message="This will change the ticket status to 'In Progress'. Continue?"
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          confirmText="Start Work"
        />
      ),
      markPending: (
        <FormDialog
          title="Mark as Pending"
          description="Provide a reason for marking this ticket as pending"
          fields={[
            { name: "reason", label: "Pending Reason", type: "textarea", placeholder: "Explain why this ticket is being put on hold...", required: true, value: formData.reason, onChange: (v: string) => setFormData(prev => ({ ...prev, reason: v as string })) } as FormField<string>
          ]}
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          error={actionDialog.error}
          confirmText="Mark Pending"
        />
      ),
      resolve: (
        <FormDialog
          title="Resolve Ticket"
          description="Provide a resolution summary"
          fields={[
            { name: "resolutionSummary", label: "Resolution Summary", type: "textarea", placeholder: "Describe how this issue was resolved...", required: true, value: formData.resolutionSummary, onChange: (v: string) => setFormData(prev => ({ ...prev, resolutionSummary: v as string })) } as FormField<string>
          ]}
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          error={actionDialog.error}
          confirmText="Resolve"
        />
      ),
      reopen: (
        <FormDialog
          title="Reopen Ticket"
          description="Optional: Provide a reason for reopening"
          fields={[
            { name: "reason", label: "Reopen Reason (Optional)", type: "textarea", placeholder: "Why is this ticket being reopened?", required: false, value: formData.reason, onChange: (v: string) => setFormData(prev => ({ ...prev, reason: v as string })) } as FormField<string>
          ]}
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          error={actionDialog.error}
          confirmText="Reopen"
        />
      ),
      close: (
        <ConfirmDialog
          title="Close Ticket"
          message="This will permanently close the ticket. Only resolved tickets can be closed. Continue?"
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          confirmText="Close Ticket"
          variant="destructive"
        />
      ),
      escalate: (
        <FormDialog
          title="Escalate Ticket"
          description="Select a user to escalate to and provide a reason"
          fields={[
            { name: "escalatedTo", label: "Escalate To", type: "select", options: technicians.map(t => ({ value: t.id, label: `${t.name} (${t.role})` })), required: true, value: formData.escalatedTo, onChange: (v: string) => setFormData(prev => ({ ...prev, escalatedTo: v === "" ? null : Number(v) })) } as FormField<number | null>,
            { name: "escalationReason", label: "Escalation Reason", type: "textarea", placeholder: "Explain why this ticket needs escalation...", required: true, value: formData.escalationReason, onChange: (v: string) => setFormData(prev => ({ ...prev, escalationReason: v as string })) } as FormField<string>
          ]}
          onConfirm={handleActionSubmit}
          onCancel={closeActionDialog}
          loading={actionDialog.loading}
          error={actionDialog.error}
          confirmText="Escalate"
        />
      ),
    };

    return (
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
        initial={false}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={backdropTransition}
        onClick={closeActionDialog}
      >
        <motion.div
          className="w-full max-w-md rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
          onClick={(e) => e.stopPropagation()}
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={modalTransition}
        >
          {dialogs[actionDialog.type]}
        </motion.div>
      </motion.div>
    );
  };

  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
      initial={false}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={backdropTransition}
    >
      <motion.div
        className="w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-slate-900"
        onClick={(e) => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={modalTransition}
      >
        {/* Header */}
        <div className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-200 bg-white px-8 py-6 dark:border-slate-800 dark:bg-slate-900">
          <div>
            <motion.h2
              className="text-3xl font-bold text-slate-900 dark:text-white"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              Ticket Details
            </motion.h2>
            <motion.p
              className="mt-1 text-slate-500 dark:text-slate-400"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2, delay: 0.05 }}
            >
              Complete AI generated ticket information
            </motion.p>
          </div>

          <motion.button
            onClick={onClose}
            className="rounded-lg p-2 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
            whileHover={reducedMotion ? {} : { scale: 1.1 }}
            whileTap={reducedMotion ? {} : { scale: 0.9 }}
            initial={{ opacity: 0, rotate: -90 }}
            animate={{ opacity: 1, rotate: 0 }}
            transition={{ duration: 0.2, delay: 0.1 }}
          >
            <X className="text-slate-600 dark:text-white" />
          </motion.button>
        </div>

        {/* Tab Navigation */}
        <div className="sticky top-16 z-10 border-b border-slate-200 bg-white px-8 dark:border-slate-800 dark:bg-slate-900">
          <div className="flex gap-1">
            <TabButton
              active={activeTab === "details"}
              onClick={() => setActiveTab("details")}
              icon={<TicketIcon size={18} />}
              label="Details"
            />
            <TabButton
              active={activeTab === "timeline"}
              onClick={() => setActiveTab("timeline")}
              icon={<History size={18} />}
              label="Timeline"
            />
          </div>
        </div>

        {/* Content */}
        <motion.div
          className="space-y-8 p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1, ease: "easeOut" }}
        >
          {activeTab === "details" && (
            <>
              {/* Ticket */}
              <Section title="Ticket Information" icon={<TicketIcon size={20} />}>
                <Info label="Ticket ID" value={`#${ticket.id}`} />
                <BadgeInfo label="Status" value={ticket.status} className={statusColor[ticket.status as keyof typeof statusColor] ?? ""} />
                <Info label="Title" value={ticket.title} full />
                <Info label="Description" value={ticket.description} full />
              </Section>

              {/* AI */}
              <Section title="AI Analysis" icon={<Bot size={20} />}>
                <Info label="Category" value={ticket.category ?? "N/A"} />
                <Info label="Subcategory" value={ticket.subcategory ?? "N/A"} />
                <Info label="Confidence" value={ticket.confidence != null ? `${Math.round(ticket.confidence * 100)}%` : "N/A"} />
                <Info label="AI Processed" value={ticket.ai_processed ? "Yes" : "No"} />
                <motion.div className="md:col-span-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
                  <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">Keywords</p>
                  <div className="flex flex-wrap gap-2">
                    {ticket.keywords?.length ? (
                      ticket.keywords.map((word) => (
                        <motion.span
                          key={word}
                          className="rounded-full bg-blue-600 px-3 py-1 text-sm text-white"
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ type: "spring", stiffness: 400, damping: 25, delay: 0.05 }}
                        >
                          {word}
                        </motion.span>
                      ))
                    ) : (
                      <span className="text-slate-500">No keywords</span>
                    )}
                  </div>
                </motion.div>
              </Section>

              {/* Priority */}
              <Section title="Priority" icon={<Brain size={20} />}>
                <BadgeInfo label="Priority" value={ticket.priority} className={priorityColor[ticket.priority as keyof typeof priorityColor] ?? ""} />
                <Info label="Priority Reason" value={ticket.priority_reason ?? "N/A"} />
              </Section>

              {/* Assignment */}
              <Section title="Assignment" icon={<User size={20} />}>
                <Info label="Assigned To" value={ticket.assigned_name ?? "Unassigned"} />
                <Info label="Assignment Reason" value={ticket.assignment_reason ?? "N/A"} />
                {ticket.pending_reason && (
                  <Info label="Pending Reason" value={ticket.pending_reason} full />
                )}
              </Section>

              {/* Escalation */}
              {ticket.escalated_to && (
                <Section title="Escalation" icon={<AlertTriangle size={20} />}>
                  <Info label="Escalated To" value={ticket.escalated_to_name ?? `User #${ticket.escalated_to}`} />
                  <Info label="Escalated By" value={ticket.escalated_by_name ?? `User #${ticket.escalated_by}`} />
                  <Info label="Escalation Reason" value={ticket.escalation_reason ?? "N/A"} full />
                  <Info label="Escalated At" value={ticket.escalated_at ? new Date(ticket.escalated_at).toLocaleString() : "N/A"} />
                </Section>
              )}

              {/* Resolution */}
              {ticket.resolved_at && (
                <Section title="Resolution" icon={<CheckCircle size={20} />}>
                  <Info label="Resolved By" value={ticket.resolved_by_name ?? `User #${ticket.resolved_by}`} />
                  <Info label="Resolved At" value={new Date(ticket.resolved_at).toLocaleString()} />
                  <Info label="Resolution Summary" value={ticket.resolution_summary ?? "N/A"} full />
                </Section>
              )}

              {/* Metadata */}
              <Section title="Metadata" icon={<Calendar size={20} />}>
                <Info label="Created By" value={String(ticket.created_by)} />
                <Info label="Created At" value={new Date(ticket.created_at).toLocaleString()} />
              </Section>

              {/* SLA Information (Phase 2C) */}
              {(ticket.sla_policy_id || ticket.sla_response_deadline || ticket.sla_resolution_deadline) && (
                <Section title="SLA" icon={<Calendar size={20} />}>
                  {ticket.sla_policy_id && (
                    <BadgeInfo label="SLA Policy" value={`Policy #${ticket.sla_policy_id}`} className="bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400" />
                  )}
                  {ticket.sla_response_deadline && <Info label="Response Deadline" value={new Date(ticket.sla_response_deadline).toLocaleString()} />}
                  {ticket.sla_resolution_deadline && <Info label="Resolution Deadline" value={new Date(ticket.sla_resolution_deadline).toLocaleString()} />}
                  {ticket.sla_response_status && <Info label="Response Status" value={ticket.sla_response_status} />}
                  {ticket.sla_resolution_status && <Info label="Resolution Status" value={ticket.sla_resolution_status} />}
                  {ticket.sla_response_breached && <Info label="Response Breached" value="Yes" />}
                  {ticket.sla_resolution_breached && <Info label="Resolution Breached" value="Yes" />}
                </Section>
              )}

              {/* Attachments / Evidence */}
              <TicketAttachmentsPanel ticketId={ticket.id} />

              {/* Workflow Action Buttons */}
              {renderActionButtons()}
            </>
          )}

          {activeTab === "timeline" && (
            <TimelineView 
              timeline={timeline} 
              loading={timelineLoading} 
              reducedMotion={reducedMotion}
            />
          )}
        </motion.div>

        {/* Action Dialogs */}
        {renderActionDialog()}
      </motion.div>
    </motion.div>
  );
}

// Helper Components

function TabButton({ active, onClick, icon, label }: { active: boolean; onClick: () => void; icon: React.ReactNode; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all ${
        active
          ? "border-blue-600 text-blue-600 dark:text-blue-400"
          : "border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-white"
      }`}
    >
      {icon} {label}
    </button>
  );
}

interface TechnicianPickerDialogProps {
  title: string;
  description: string;
  technicians: Technician[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
  error: string | null;
}

function TechnicianPickerDialog({ title, description, technicians, selectedId, onSelect, onConfirm, onCancel, loading, error }: TechnicianPickerDialogProps) {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>
      </div>
      
      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-red-700 dark:bg-red-500/20 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="max-h-60 overflow-y-auto">
        {technicians.length === 0 ? (
          <div className="py-8 text-center text-slate-500 dark:text-slate-400">
            No technicians available
          </div>
        ) : (
          technicians.map((tech) => (
            <label
              key={tech.id}
              className={`flex items-center gap-3 p-3 rounded-lg border transition-colors cursor-pointer ${
                selectedId === tech.id
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-500/10"
                  : "border-slate-200 hover:border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
              }`}
            >
              <input
                type="radio"
                name="technician"
                value={tech.id}
                checked={selectedId === tech.id}
                onChange={() => onSelect(tech.id)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500"
              />
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 dark:text-white truncate">{tech.name}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {tech.role} • {tech.specialization ?? "General"} • {tech.workload ?? 0} active tickets
                </p>
              </div>
            </label>
          ))
        )}
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button
          onClick={onCancel}
          disabled={loading}
          className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          disabled={loading || selectedId === null}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Confirm"}
        </button>
      </div>
    </div>
  );
}

interface ConfirmDialogProps {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
  confirmText: string;
  variant?: "primary" | "destructive";
}

function ConfirmDialog({ title, message, onConfirm, onCancel, loading, confirmText, variant = "primary" }: ConfirmDialogProps) {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{message}</p>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button
          onClick={onCancel}
          disabled={loading}
          className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          disabled={loading}
          className={`px-4 py-2 rounded-lg text-white ${
            variant === "destructive"
              ? "bg-red-600 hover:bg-red-700"
              : "bg-blue-600 hover:bg-blue-700"
          } disabled:opacity-50`}
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : confirmText}
        </button>
      </div>
    </div>
  );
}

interface FormField<T = string | number | null> {
  name: string;
  label: string;
  type: "text" | "textarea" | "select";
  placeholder?: string;
  required: boolean;
  value: T;
  onChange: (value: unknown) => void;
  options?: { value: number; label: string }[];
}

interface FormDialogProps {
  title: string;
  description: string;
  fields: FormField[];
  onConfirm: () => void;
  onCancel: () => void;
  loading: boolean;
  error: string | null;
  confirmText: string;
}

function FormDialog({ title, description, fields, onConfirm, onCancel, loading, error, confirmText }: FormDialogProps) {
  return (
    <div className="p-6 space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>
      </div>

      {error && (
        <div className="rounded-lg bg-red-50 p-3 text-red-700 dark:bg-red-500/20 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {fields.map((field) => (
          <div key={field.name} className="space-y-1">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              {field.label} {field.required && <span className="text-red-500">*</span>}
            </label>
            {field.type === "select" ? (
              <select
                value={field.value ?? ""}
                onChange={(e) => field.onChange(e.target.value === "" ? null : Number(e.target.value))}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                required={field.required}
              >
                <option value="">Select...</option>
                {field.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            ) : field.type === "textarea" ? (
              <textarea
                value={field.value as string}
                onChange={(e) => field.onChange(e.target.value)}
                placeholder={field.placeholder}
                rows={4}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                required={field.required}
              />
            ) : (
              <input
                type="text"
                value={field.value as string}
                onChange={(e) => field.onChange(e.target.value)}
                placeholder={field.placeholder}
                className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-900 outline-none transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-200 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
                required={field.required}
              />
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button
          onClick={onCancel}
          disabled={loading}
          className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : confirmText}
        </button>
      </div>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="mb-5 flex items-center gap-3">
        <motion.div
          className="rounded-lg bg-blue-600 p-2 text-white"
          initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
          animate={{ opacity: 1, scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 400, damping: 25 }}
        >
          {icon}
        </motion.div>
        <motion.h3
          className="text-xl font-semibold text-slate-900 dark:text-white"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          {title}
        </motion.h3>
      </div>
      <div className="grid gap-5 md:grid-cols-2">{children}</div>
    </motion.div>
  );
}

function Info({ label, value, full = false }: { label: string; value: string; full?: boolean }) {
  return (
    <motion.div className={full ? "md:col-span-2" : ""} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.05 }}>
      <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 dark:border-slate-700 dark:bg-slate-800 dark:text-white">
        {value}
      </div>
    </motion.div>
  );
}

function BadgeInfo({ label, value, className }: { label: string; value: string; className: string }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.05 }}>
      <p className="mb-2 text-sm text-slate-500 dark:text-slate-400">{label}</p>
      <span className={`rounded-full px-3 py-1 text-sm font-semibold ${className}`}>{value}</span>
    </motion.div>
  );
}

function TimelineView({ timeline, loading, reducedMotion }: { timeline: TimelineItem[]; loading: boolean; reducedMotion: boolean }) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-3 text-slate-500">Loading timeline...</span>
      </div>
    );
  }

  if (timeline.length === 0) {
    return (
      <div className="text-center py-12">
        <History className="w-12 h-12 mx-auto text-slate-300 dark:text-slate-600" />
        <p className="mt-3 text-slate-500 dark:text-slate-400">No timeline events yet</p>
      </div>
    );
  }

  const getEventIcon = (type: TimelineItemType) => {
    switch (type) {
      case "HISTORY": return <Clock className="w-5 h-5 text-blue-600" />;
      case "COMMENT": return <MessageSquare className="w-5 h-5 text-green-600" />;
      case "INTERNAL_NOTE": return <MessageSquare className="w-5 h-5 text-orange-600" />;
      case "ATTACHMENT": return <Paperclip className="w-5 h-5 text-purple-600" />;
    }
  };

  const getEventTitle = (item: TimelineItem) => {
    if (item.type === "COMMENT" || item.type === "INTERNAL_NOTE") {
      return item.type === "INTERNAL_NOTE" ? "Internal Note" : "Comment";
    }
    if (item.type === "ATTACHMENT") {
      return `Attachment: ${item.filename}`;
    }
    return item.event_type?.replace(/_/g, " ") || "History Event";
  };

  return (
    <div className="space-y-6">
      {timeline.map((item) => (
        <motion.div
          key={item.id}
          className="flex gap-4"
          initial={reducedMotion ? false : { opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          <div className="relative flex-shrink-0">
            <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
              {getEventIcon(item.type)}
            </div>
            <div className="absolute left-1/2 top-10 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700 -translate-x-1/2" />
          </div>
          <div className="flex-1 min-w-0 pt-1">
            <div className="flex items-center gap-3">
              <span className="font-medium text-slate-900 dark:text-white">{getEventTitle(item)}</span>
              {item.is_internal && (
                <span className="rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700 dark:bg-orange-500/20 dark:text-orange-400">
                  Internal
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
              {item.actor_name || `User #${item.actor_id}`} • {new Date(item.timestamp).toLocaleString()}
            </p>
            {item.body && (
              <p className="mt-2 text-slate-900 dark:text-white whitespace-pre-wrap">{item.body}</p>
            )}
            {item.old_value && item.new_value && item.old_value !== item.new_value && (
              <div className="mt-2 space-y-1">
                <div className="text-xs text-red-600 dark:text-red-400">
                  <span className="font-medium">From:</span> {item.old_value}
                </div>
                <div className="text-xs text-green-600 dark:text-green-400">
                  <span className="font-medium">To:</span> {item.new_value}
                </div>
              </div>
            )}
            {item.new_value && !item.old_value && (
              <p className="mt-2 text-xs text-green-600 dark:text-green-400">{item.new_value}</p>
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}