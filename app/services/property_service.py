from app.models.property import Property
from app.extensions import db
from app.repositories.sqlalchemy.property_repo_sql import SqlPropertyRepo
from werkzeug.datastructures import FileStorage
from app.services.upload_service import UploadService
from app.services.location_service import LocationService


# แก้ไขชื่อคลาสจาก propertyService เป็น PropertyService
class PropertyService:
    def __init__(self, repo: SqlPropertyRepo, upload_service: UploadService, location_service: LocationService):
        self.repo = repo
        self.upload_service = upload_service
        self.location_service = location_service

    def create(self, owner_id: int, data: dict) -> Property:
        # แยกข้อมูลตำแหน่งออกมา
        location_data = {
            "address": data.get("address"),
            "road": data.get("road"),
            "subdistrict": data.get("subdistrict"),
            "district": data.get("district"),
            "province": data.get("province"),
            "zip_code": data.get("zip_code")
        }

        # หาค่า lat, lng จาก LocationService
        lat, lng = self.location_service.get_lat_lng(location_data)

        # สร้าง Property object พร้อมข้อมูล lat, lng
        prop = Property(owner_id=owner_id, lat=lat, lng=lng, **data)
        
        return self.repo.add(prop)

    def update(self, owner_id: int, prop_id: int, data: dict):
        prop = self.repo.get(prop_id)
        if not prop or prop.owner_id != owner_id:
            return None
        
        # แยกข้อมูลตำแหน่งออกมาเพื่ออัปเดต
        location_data = {
            "address": data.get("address"),
            "road": data.get("road"),
            "subdistrict": data.get("subdistrict"),
            "district": data.get("district"),
            "province": data.get("province"),
            "zip_code": data.get("zip_code")
        }
        
        # หาค่า lat, lng ใหม่จาก LocationService
        lat, lng = self.location_service.get_lat_lng(location_data)
        data['lat'] = lat
        data['lng'] = lng

        for k,v in data.items():
            setattr(prop, k, v)
        self.repo.save(prop)
        return prop

    def get_by_id(self, prop_id: int):
        return self.repo.get(prop_id)

    def add_image(self, prop: Property, image_file: FileStorage) -> Property:
        path = self.upload_service.save_image(prop.owner_id, image_file)
        prop.add_image(path)
        self.repo.save(prop)
        return prop

    def delete_image(self, prop: Property, image_id: int) -> bool:
        image = prop.find_image(image_id)
        if image:
            self.upload_service.delete_image(image.file_path)
            prop.remove_image(image_id)
            self.repo.save(prop)
            return True
        return False

    def reorder_images(self, prop: Property, image_ids: list[int]):
        prop.reorder_images(image_ids)
        self.repo.save(prop)

    def soft_delete(self, prop: Property):
        prop.soft_delete()
        self.repo.save(prop)

    def restore(self, prop: Property):
        prop.restore()
        self.repo.save(prop)