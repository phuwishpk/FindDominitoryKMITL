from collections import OrderedDict
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Property, Owner

class DashboardService:
    def __init__(self, user_repo, property_repo, approval_repo):
        self.user_repo = user_repo
        self.property_repo = property_repo
        self.approval_repo = approval_repo

    def get_stats(self) -> dict:
        """รวบรวมสถิติหลักของระบบ"""
        return {
            "total_owners": self.user_repo.count_active_owners(),
            "total_properties": self.property_repo.count_active_properties(),
            "pending_properties": len(self.approval_repo.get_pending_properties()),
            "pending_owners": len(self.user_repo.get_pending_owners())
        }

    def get_pie_chart_data(self) -> dict:
        """ดึงข้อมูลสำหรับ Pie Chart (Top 5 ถนน)"""
        pie_data_query = self.property_repo.get_property_counts_by_road(limit=5)
        return {
            "labels": [item.road for item in pie_data_query],
            "data": [item.count for item in pie_data_query]
        }

    def get_line_chart_data(self) -> dict:
        """ดึงข้อมูลสำหรับ Line Chart (6 เดือนล่าสุด)"""
        labels, owner_data, prop_data = [], OrderedDict(), OrderedDict()
        today = datetime.utcnow()
        for i in range(5, -1, -1):
            month_date = today - timedelta(days=i * 30)
            month_key = month_date.strftime("%b %Y")
            labels.append(month_key)
            owner_data[month_key] = self.user_repo.count_owners_by_month(month_date)
            prop_data[month_key] = self.property_repo.count_properties_by_month(month_date)
        
        return {
            "labels": labels,
            "owners": list(owner_data.values()),
            "properties": list(prop_data.values())
        }