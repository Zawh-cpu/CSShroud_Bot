import qrcode
import io


class QRMaker:
    @staticmethod
    def get_from_str(data: str):
        qr = qrcode.main.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=4,
        )

        qr.add_data(data)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer)

        buffer.seek(0)

        return buffer
