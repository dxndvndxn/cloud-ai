import { type TreeNodeProps } from '@snack-uikit/tree';
import { FolderSVG, FileSVG } from '@snack-uikit/icons';
import type { SelectFileArgs } from '../store';

export const structureFilesAdapter = (
  obj: Record<string, any>,
  callee: (value: SelectFileArgs) => void,
  parentPath = '',
) => {
  const result: TreeNodeProps[] = [];

  for (const [key, value] of Object.entries(obj)) {
    const id = parentPath ? `${parentPath}/${key}` : key;
    const title = key;

    let nested: TreeNodeProps[] = [];
    let isLeaf = true;

    // Если значение — объект (и не строка), значит, есть дети
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      nested = structureFilesAdapter(value, callee, id);
      isLeaf = false;
    }

    const item: TreeNodeProps = {
      id,
      title,
      nested,
    };

    if (!isLeaf) {
      item.nested = nested;
      // @ts-ignore
      item.icon = <FolderSVG />;
    } else {
      // @ts-ignore
      item.nested = undefined;
      // @ts-ignore
      item.icon = <FileSVG />;
      item.onClick = () => callee({ selectedFile: value, selectedFileName: title });
    }

    result.push(item);
  }

  return result;
};
