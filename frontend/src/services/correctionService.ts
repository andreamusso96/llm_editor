// src/services/apiService.ts
import axios from 'axios';
import type { PromptList, CorrectionCreateRequest, CorrectionCreateResponse, CorrectionStatusResponse, CorrectionResultResponse } from '../types/api'; // Make sure this path is correct


const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const fetchPrompts = async (): Promise<PromptList> => {
  try {
    console.log(`Fetching prompts from ${API_BASE_URL}/prompts`);
    const response = await axios.get<PromptList>(`${API_BASE_URL}/prompts`);
    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching prompts:", error);
    // You might want to throw the error or return a default/empty list
    // For now, let's re-throw to be handled by the calling component
    throw error;
  }
};

export const submitCorrection = async (textContent: string, promptIdRefs: string[]): Promise<CorrectionCreateResponse> => {
    try {

      const requestBody: CorrectionCreateRequest = {
        text_content: textContent,
        prompt_id_refs: promptIdRefs,
      };
      const response = await axios.post<CorrectionCreateResponse>(
        `${API_BASE_URL}/corrections`,
        requestBody
      );
      return response.data;
    } catch (error) {
      console.error("Error submitting correction:", error);
      // You might want more specific error handling or reformatting here
      throw error; // Re-throw to be handled by the calling component
    }
  };


  export const getCorrectionStatus = async (correctionId: number): Promise<CorrectionStatusResponse> => {
    try {
      const response = await axios.get<CorrectionStatusResponse>(
        `${API_BASE_URL}/corrections/${correctionId}/status`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching status for correction ID ${correctionId}:`, error);
      throw error; 
    }
  };


  // New function to get the full correction results
export const getCorrectionResult = async (
    correctionId: number
  ): Promise<CorrectionResultResponse> => {
    try {
      const response = await axios.get<CorrectionResultResponse>(
        `${API_BASE_URL}/corrections/${correctionId}/results`
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching results for correction ID ${correctionId}:`, error);
      throw error; // Re-throw to be handled by the calling component
    }
  };
  

// We will add more API functions here later (submitCorrection, getCorrectionStatus, etc.)