from sqlalchemy.orm import Session
from datetime import datetime
from app.models.ml_status import MLStatus

class MLStatusService:
    @staticmethod
    def get_status(db: Session) -> MLStatus:
        """
        Mengambil status ML saat ini. Jika belum ada, buat baru.
        """
        status = db.query(MLStatus).filter(MLStatus.id == 1).first()
        if not status:
            status = MLStatus(id=1, needs_retrain=True, model_status="OUTDATED", model_version=0)
            db.add(status)
            db.commit()
            db.refresh(status)
        return status

    @staticmethod
    def mark_needs_retrain(db: Session) -> None:
        """
        Menandai bahwa model perlu di-retrain karena ada perubahan pada dataset (harga, rating, sold).
        """
        status = MLStatusService.get_status(db)
        if not status.needs_retrain:
            status.needs_retrain = True
            status.last_dataset_update = datetime.utcnow()
            status.model_status = "OUTDATED"
            db.commit()

    @staticmethod
    def mark_retrain_success(db: Session) -> None:
        """
        Menandai bahwa model berhasil di-retrain.
        Fungsi ini dipanggil setelah endpoint CBF berhasil dieksekusi.
        """
        status = MLStatusService.get_status(db)
        status.needs_retrain = False
        status.last_trained_at = datetime.utcnow()
        status.model_status = "READY"
        status.model_version += 1
        db.commit()
