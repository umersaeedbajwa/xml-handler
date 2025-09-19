import { Card, Statistic, Row, Col } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

interface StatsCardProps {
  title: string;
  value: number | string;
  precision?: number;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  valueStyle?: React.CSSProperties;
  loading?: boolean;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

const StatsCard = ({
  title,
  value,
  precision,
  prefix,
  suffix,
  valueStyle,
  loading = false,
  trend,
}: StatsCardProps) => {
  return (
    <Card loading={loading}>
      <Row>
        <Col span={trend ? 18 : 24}>
          <Statistic
            title={title}
            value={value}
            precision={precision}
            prefix={prefix}
            suffix={suffix}
            valueStyle={valueStyle}
          />
        </Col>
        {trend && (
          <Col span={6}>
            <Statistic
              value={trend.value}
              precision={2}
              valueStyle={{ 
                color: trend.isPositive ? '#3f8600' : '#cf1322',
                fontSize: '14px',
              }}
              prefix={trend.isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix="%"
            />
          </Col>
        )}
      </Row>
    </Card>
  );
};

export default StatsCard;
