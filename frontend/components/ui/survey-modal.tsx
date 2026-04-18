"use client";

import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface SurveyModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  userId: string;
  recommendationId: string;
  itemsShown: string[];
  onSubmit?: () => void;
}

export function SurveyModal({
  open,
  onOpenChange,
  userId,
  recommendationId,
  itemsShown,
  onSubmit,
}: SurveyModalProps) {
  const [serendipity, setSerendipity] = useState<number | null>(null);
  const [diversity, setDiversity] = useState<number | null>(null);
  const [satisfaction, setSatisfaction] = useState<number | null>(null);
  const [preferenceVsExploration, setPreferenceVsExploration] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const allAnswered = serendipity !== null && diversity !== null && satisfaction !== null && preferenceVsExploration !== null;

  const handleSubmit = async () => {
    if (!allAnswered) {
      alert("Please answer all questions");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        user_id: userId,
        recommendation_id: recommendationId,
        items_shown: itemsShown,
        serendipity_rating: serendipity,
        diversity_rating: diversity,
        satisfaction_rating: satisfaction,
        preference_vs_exploration: preferenceVsExploration,
      };

      const response = await fetch("/api/surveys", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const error = await response.text();
        console.error("Survey error response:", error);
        throw new Error(`Failed to submit survey: ${response.status}`);
      }

      const data = await response.json();
      console.log("Survey submitted:", data);
      
      onOpenChange(false);
      if (onSubmit) {
        onSubmit();
      }
    } catch (error) {
      console.error("Error submitting survey:", error);
      alert("Failed to submit survey. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenChange = (newOpen: boolean) => {
    if (!submitting) {
      onOpenChange(newOpen);
    }
  };

  const scale_1_to_5 = [
    { value: "1", label: "Very Poor" },
    { value: "2", label: "Poor" },
    { value: "3", label: "Average" },
    { value: "4", label: "Good" },
    { value: "5", label: "Excellent" },
  ];

  const scale_1_to_10 = Array.from({ length: 10 }, (_, i) => ({
    value: String(i + 1),
    label: i + 1,
  }));

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Recommendation Feedback</DialogTitle>
          <DialogDescription>
            Help us improve by rating these recommendations (1 minute)
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Q1: Relevance */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">
              Q1. How relevant were these recommendations to your interests?
            </Label>
            <RadioGroup
              value={serendipity?.toString() || ""}
              onValueChange={(val) => setSerendipity(parseInt(val))}
            >
              <div className="flex flex-col gap-2">
                {scale_1_to_5.map((option) => (
                  <div key={option.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={option.value} id={`serendipity-${option.value}`} />
                    <Label htmlFor={`serendipity-${option.value}`} className="cursor-pointer font-normal">
                      {option.value} - {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          </div>

          {/* Q2: Diversity */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">
              Q2. How much diversity and exploration in these recommendations?
            </Label>
            <RadioGroup
              value={diversity?.toString() || ""}
              onValueChange={(val) => setDiversity(parseInt(val))}
            >
              <div className="flex flex-col gap-2">
                {scale_1_to_5.map((option) => (
                  <div key={option.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={option.value} id={`diversity-${option.value}`} />
                    <Label htmlFor={`diversity-${option.value}`} className="cursor-pointer font-normal">
                      {option.value} - {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          </div>

          {/* Q3: Satisfaction */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">
              Q3. How happy are you with these recommendations overall?
            </Label>
            <RadioGroup
              value={satisfaction?.toString() || ""}
              onValueChange={(val) => setSatisfaction(parseInt(val))}
            >
              <div className="flex flex-col gap-2">
                {scale_1_to_5.map((option) => (
                  <div key={option.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={option.value} id={`satisfaction-${option.value}`} />
                    <Label htmlFor={`satisfaction-${option.value}`} className="cursor-pointer font-normal">
                      {option.value} - {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          </div>

          {/* Q4: Preference vs Exploration */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">
              Q4. Would you like more diversity or more of preferred categories?
            </Label>
            <p className="text-sm text-gray-200 mb-2">
              <span className="font-bold">1</span> = Show me more from my preferred categories | 
              <span className="font-bold">10</span> = More random exploration
            </p>
            <RadioGroup
              value={preferenceVsExploration?.toString() || ""}
              onValueChange={(val) => setPreferenceVsExploration(parseInt(val))}
            >
              <div className="grid grid-cols-5 gap-2">
                {scale_1_to_10.map((option) => (
                  <div key={option.value} className="flex flex-col items-center space-y-1">
                    <RadioGroupItem value={option.value} id={`pref-expl-${option.value}`} />
                    <Label htmlFor={`pref-expl-${option.value}`} className="cursor-pointer font-normal text-xs">
                      {option.label}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={submitting}
            className="flex-1"
          >
            Skip
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting || !allAnswered}
            className="flex-1"
          >
            {submitting ? "Submitting..." : "Submit"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
