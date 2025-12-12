export type TestCasesWS = {
  directory_structure?: Record<string, any>;
  test_plan?: string;
  type?: string;
  message?: string;
  status?: string;
};

export interface CreateTestCaseResponse {
  success: boolean;
}
