import { makeAutoObservable } from 'mobx';
import type { TestCasesWS } from '../../../types';

export class TestCasesStore implements TestCasesWS {
  directory_structure: TestCasesWS['directory_structure'] = undefined;
  test_plan: TestCasesWS['test_plan'] = '';
  selectedFile = '';
  selectedFileName = '';

  constructor() {
    makeAutoObservable(this);
  }

  setTestCases = ({ directory_structure, test_plan }: TestCasesWS) => {
    // убирает косые ковычки в начале и в конце строки
    const cutTestPlan = test_plan?.replace(/^`+|`+$/g, '');
    this.directory_structure = directory_structure || this.directory_structure;
    this.test_plan = cutTestPlan || this.test_plan;
  };

  selectFile = ({ selectedFile, selectedFileName }: SelectFileArgs) => {
    this.selectedFile = selectedFile;
    this.selectedFileName = selectedFileName;
  };

  clearCases = () => {
    this.selectedFile = '';
    this.selectedFileName = '';
    this.test_plan = '';
    this.directory_structure = undefined;
  }
}

export interface SelectFileArgs {
  selectedFile: string;
  selectedFileName: string;
}
