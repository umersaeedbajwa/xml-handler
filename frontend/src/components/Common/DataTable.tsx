import { Table, Card, Button, Space, Input, Select } from 'antd';
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons';
import type { TableProps } from '../../types';

const { Option } = Select;

interface DataTableProps<T = any> extends TableProps<T> {
  title?: string;
  showSearch?: boolean;
  searchPlaceholder?: string;
  searchValue?: string;
  onSearch?: (value: string) => void;
  showRefresh?: boolean;
  onRefresh?: () => void;
  showCreate?: boolean;
  onCreate?: () => void;
  createButtonText?: string;
  filters?: {
    key: string;
    label: string;
    options: { label: string; value: string }[];
    value?: string;
    onChange: (value: string) => void;
  }[];
  size?: 'small' | 'middle' | 'large';
  bordered?: boolean;
  showPagination?: boolean;
}

const DataTable = <T extends Record<string, any>>({
  title,
  columns,
  data,
  loading = false,
  showSearch = true,
  searchPlaceholder = 'Search...',
  searchValue,
  onSearch,
  showRefresh = true,
  onRefresh,
  showCreate = false,
  onCreate,
  createButtonText = 'Create',
  filters = [],
  pagination,
  onPaginationChange,
  rowSelection,
  size = 'middle',
  bordered = true,
  showPagination = true,
}: DataTableProps<T>) => {
  const tableColumns = columns.map(col => ({
    key: col.key,
    title: col.title,
    dataIndex: col.dataIndex as string,
    render: col.render,
    sorter: col.sortable ? (a: T, b: T) => {
      const aVal = a[col.dataIndex];
      const bVal = b[col.dataIndex];
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return aVal.localeCompare(bVal);
      }
      return aVal - bVal;
    } : undefined,
    width: col.width,
  }));

  const handleTableChange = (paginationInfo: any) => {
    if (onPaginationChange) {
      onPaginationChange(paginationInfo.current, paginationInfo.pageSize);
    }
  };

  const paginationConfig = showPagination && pagination ? {
    current: pagination.page,
    pageSize: pagination.pageSize,
    total: pagination.total,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total: number, range: [number, number]) => 
      `${range[0]}-${range[1]} of ${total} items`,
    pageSizeOptions: ['10', '20', '50', '100'],
  } : false;

  return (
    <Card 
      title={title}
      extra={
        <Space>
          {showSearch && (
            <Input.Search
              placeholder={searchPlaceholder}
              value={searchValue}
              onChange={(e) => onSearch?.(e.target.value)}
              onSearch={onSearch}
              style={{ width: 200 }}
              allowClear
            />
          )}
          {filters.map(filter => (
            <Select
              key={filter.key}
              placeholder={filter.label}
              value={filter.value}
              onChange={filter.onChange}
              style={{ width: 120 }}
              allowClear
            >
              {filter.options.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          ))}
          {showRefresh && (
            <Button
              icon={<ReloadOutlined />}
              onClick={onRefresh}
              title="Refresh"
            />
          )}
          {showCreate && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={onCreate}
            >
              {createButtonText}
            </Button>
          )}
        </Space>
      }
      styles={{ body: { padding: 0 } }}
    >
      <Table
        columns={tableColumns}
        dataSource={data}
        loading={loading}
        rowSelection={rowSelection}
        pagination={paginationConfig}
        onChange={handleTableChange}
        size={size}
        bordered={bordered}
        scroll={{ x: 'max-content' }}
        rowKey={(record) => record.id || record.uuid || record.key}
      />
    </Card>
  );
};

export default DataTable;
