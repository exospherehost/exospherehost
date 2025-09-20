'use client';

import React from 'react';
import { UpsertGraphTemplateResponse } from '@/types/state-manager';
import { GraphTemplateDetail } from '@/components/GraphTemplateDetail';

interface GraphTemplateDetailModalProps {
  graphTemplate: UpsertGraphTemplateResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export const GraphTemplateDetailModal: React.FC<GraphTemplateDetailModalProps> = ({
  graphTemplate,
  isOpen,
  onClose
}) => {
  if (!isOpen || !graphTemplate) return null;

  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <GraphTemplateDetail
          graphTemplate={graphTemplate}
          isOpen={isOpen}
          onClose={onClose}
        />
      </div>
    </div>
  );
};
