'use client';

import React, { useEffect, useRef, useState } from 'react';
import { AnimatePresence, type MotionProps, motion } from 'motion/react';
import { useAgent, useSessionContext, useSessionMessages } from '@livekit/components-react';
import { AgentChatTranscript } from '@/components/agents-ui/agent-chat-transcript';
import {
  AgentControlBar,
  type AgentControlBarControls,
} from '@/components/agents-ui/agent-control-bar';
import { Shimmer } from '@/components/ai-elements/shimmer';
import { cn } from '@/lib/shadcn/utils';
import { TileLayout } from './tile-view';

const MotionMessage = motion.create(Shimmer);

const BOTTOM_VIEW_MOTION_PROPS: MotionProps = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

const CHAT_MOTION_PROPS: MotionProps = {
  variants: {
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeOut',
        duration: 0.3,
      },
    },
    visible: {
      opacity: 1,
      transition: {
        delay: 0.2,
        ease: 'easeOut',
        duration: 0.3,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

const SHIMMER_MOTION_PROPS: MotionProps = {
  variants: {
    visible: {
      opacity: 1,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0.8,
      },
    },
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

export interface AgentSessionView_01Props {
  /**
   * Message shown above the controls before the first chat message is sent.
   *
   * @default 'Agent is listening, ask it a question'
   */
  preConnectMessage?: string;
  /**
   * Enables or disables the chat toggle and transcript input controls.
   *
   * @default true
   */
  supportsChatInput?: boolean;
  /**
   * Enables or disables camera controls in the bottom control bar.
   *
   * @default true
   */
  supportsVideoInput?: boolean;
  /**
   * Enables or disables screen sharing controls in the bottom control bar.
   *
   * @default true
   */
  supportsScreenShare?: boolean;
  /**
   * Shows a pre-connect buffer state with a shimmer message before messages appear.
   *
   * @default true
   */
  isPreConnectBufferEnabled?: boolean;

  /** Selects the visualizer style rendered in the main tile area. */
  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  /** Primary hex color used by supported audio visualizer variants. */
  audioVisualizerColor?: `#${string}`;
  /** Hue shift intensity used by certain visualizers. */
  audioVisualizerColorShift?: number;
  /** Number of bars to render when `audioVisualizerType` is `bar`. */
  audioVisualizerBarCount?: number;
  /** Number of rows in the visualizer when `audioVisualizerType` is `grid`. */
  audioVisualizerGridRowCount?: number;
  /** Number of columns in the visualizer when `audioVisualizerType` is `grid`. */
  audioVisualizerGridColumnCount?: number;
  /** Number of radial bars when `audioVisualizerType` is `radial`. */
  audioVisualizerRadialBarCount?: number;
  /** Base radius of the radial visualizer when `audioVisualizerType` is `radial`. */
  audioVisualizerRadialRadius?: number;
  /** Stroke width of the wave path when `audioVisualizerType` is `wave`. */
  audioVisualizerWaveLineWidth?: number;
  /** Optional class name merged onto the outer `<section>` container. */
  className?: string;
}

export function AgentSessionView_01({
  preConnectMessage = 'Agent is listening, ask it a question',
  supportsChatInput = true,
  supportsVideoInput = true,
  supportsScreenShare = true,
  isPreConnectBufferEnabled = true,

  audioVisualizerType,
  audioVisualizerColor,
  audioVisualizerColorShift,
  audioVisualizerBarCount,
  audioVisualizerGridRowCount,
  audioVisualizerGridColumnCount,
  audioVisualizerRadialBarCount,
  audioVisualizerRadialRadius,
  audioVisualizerWaveLineWidth,
  ref,
  className,
  ...props
}: React.ComponentProps<'section'> & AgentSessionView_01Props) {
  const session = useSessionContext();
  const { messages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { state: agentState } = useAgent();

const getAgentStatus = () => {
  switch (agentState) {
    case 'listening':
      return {
        label: 'Listening to you',
        description: "Go ahead, I'm listening.",
      };

    case 'speaking':
      return {
        label: 'Agent is speaking',
        description: 'Please wait while I respond.',
      };

    case 'thinking':
      return {
        label: 'Thinking...',
        description: "I'm preparing a response.",
      };

    default:
      return {
        label: 'Connected',
        description: 'You can start talking.',
      };
  }
};

const agentStatus = getAgentStatus();

const controls: AgentControlBarControls = {
  leave: true,
  microphone: true,
  chat: supportsChatInput,
  camera: supportsVideoInput,
  screenShare: supportsScreenShare,
};

  return (
    <section
  ref={ref}
  className={cn(
    'relative z-10 h-full w-full overflow-hidden bg-[#f7f9fc] text-slate-900',
    className
  )}
  {...props}
>
  <header className="absolute left-0 right-0 top-0 z-50 flex h-16 items-center justify-between border-b bg-white px-6 shadow-sm">
  <div className="flex items-center gap-3">
    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-green-600 text-lg">
      🇮🇳
    </div>

    <div>
      <p className="text-sm font-bold text-slate-800">
        Jan Sahay
      </p>
      <p className="text-[10px] text-slate-400">
        AI Citizen Voice Assistant
      </p>
    </div>
  </div>

  <select
    className="rounded-lg border bg-white px-3 py-2 text-xs font-medium text-slate-700 outline-none"
    defaultValue="English"
  >
    <option>English</option>
    <option>हिन्दी</option>
    <option>Odia</option>
    <option>Bengali</option>
  </select>
</header>
      <Fade top className="absolute inset-x-4 top-0 z-10 h-40" />
      {/* transcript */}

     <div className="flex h-full w-full flex-col bg-[#f5f7fa] pt-16">

  {/* Main split screen */}
  <div className="grid min-h-0 flex-1 grid-cols-1 gap-5 p-5 md:grid-cols-2">

    {/* LEFT — AGENT */}
    <div className="flex min-h-0 flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">

      {/* Avatar */}
      <div className="flex h-32 w-32 items-center justify-center rounded-full border-4 border-white bg-gradient-to-br from-green-100 to-blue-100 text-7xl shadow-lg">
        👨‍💼
      </div>

      <h2 className="mt-5 text-xl font-bold text-slate-800">
        Jan Sahay
      </h2>

      <p className="mt-1 text-sm font-medium text-slate-500">
        {agentStatus.label}
      </p>

      <p className="mt-1 text-xs text-slate-400">
        {agentStatus.description}
      </p>

      {/* Waveform */}
      <div className="mt-8 flex h-20 items-center gap-2">
        {[0, 1, 2, 3, 4].map((bar) => (
          <motion.div
            key={bar}
            animate={
              agentState === 'listening' ||
              agentState === 'speaking'
                ? { height: [18, 45, 25, 60, 20] }
                : { height: 18 }
            }
            transition={{
              duration: 0.8,
              repeat:
                agentState === 'listening' ||
                agentState === 'speaking'
                  ? Infinity
                  : 0,
              delay: bar * 0.1,
            }}
            className="w-2 rounded-full bg-[#159447]"
          />
        ))}
      </div>

    </div>

    {/* RIGHT — TRANSCRIPT */}
    <div className="flex min-h-0 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

      {/* Transcript header */}
      <div className="flex items-center justify-between border-b px-5 py-4">

        <div>
          <h2 className="text-sm font-bold text-slate-800">
            LIVE TRANSCRIPT
          </h2>

          <p className="mt-1 text-xs text-slate-400">
            Conversation with Jan Sahay
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-green-500" />
          <span className="text-xs font-semibold text-green-600">
            LIVE
          </span>
        </div>

      </div>

      {/* Messages */}
      <div className="min-h-0 flex-1 overflow-y-auto p-5">

       <AgentChatTranscript
  agentState={agentState}
  messages={messages}
  className="
    w-full
    [&_*]:text-slate-800

    [&_.is-user>div]:bg-slate-800
    [&_.is-user>div]:text-white
    [&_.is-user>div_*]:text-white

    [&_.is-agent>div]:bg-slate-100
    [&_.is-agent>div]:text-slate-800
    [&_.is-agent>div_*]:text-slate-800

    [&_.is-user>div]:rounded-2xl
    [&_.is-agent>div]:rounded-2xl
  "
/>

      </div>

    </div>

  </div>

  {/* Existing controls */}
  <div className="shrink-0 border-t bg-white p-3">
    <AgentControlBar
      variant="livekit"
      controls={controls}
      isChatOpen={chatOpen}
      isConnected={session.isConnected}
      onDisconnect={session.end}
      onIsChatOpenChange={setChatOpen}
    />
  </div>

</div>
      
      
    </section>
  );
}
