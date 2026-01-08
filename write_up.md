# write-up-task-1
## Kiến thức học được về fsop
- Đầu tiên thì em học được về cấu trúc của 1 file structure sẽ bao gồm các thành phần chính trong ảnh dưới đây
<img width="1723" height="839" alt="image" src="https://github.com/user-attachments/assets/9e422a4c-5be5-469a-a1ca-cf0c4846797c" />
- 1 số kiến thức cần chú ý là các loại ptr
- Mỗi loại ptr đều có 1 mục tiêu sử dụng riêng
- Và em có thể sử dụng chúng để thực hiện 1 trong 2 hành động là leak data hoặc ghi đè lên vùng mong muốn
### Arbitrary read
- Trước tiên thì hãy tìm hiểu cách để ghi đè lên 1 vùng mong muốn
- Để làm v thì em cần đáp ứng 1 vài điều kiện nhất định
<img width="1225" height="715" alt="image" src="https://github.com/user-attachments/assets/83de59bc-9ed0-478f-8662-bfd6ccb0e796" />
- Đối với các ptr thì chỉ cần thỏa các điều kiện này là đc, các ptr khác thì sao cũng được
- Bth để cho đẹp mắt thì có thể set về null nhưng nếu ko cần lắm thì em sẽ giữ nguyên như trong chall lần này
<img width="1781" height="689" alt="image" src="https://github.com/user-attachments/assets/3eb4e6a0-0717-4aef-a37d-8668ad4915cf" />
- Như ảnh ở trên thì cách phương pháp này hoạt động khá đơn giản, nhưng vì em mới học nên tốn khá nhiều thời gian làm quen
- Có điều cần lưu ý là buf end - buf base phải > số bytes mà chương trình cho phép em input
- Lý do là vì vùng buf phải đủ lớn để chứa các input từ user hoặc program nhập vào, nếu ko đủ thì program sẽ tạo 1 vùng buff khác --> ko phải vùng em muốn nhập vào
- Và  các ptr khác có thể là null cx ko sao khi các điều kiện trên thỏa
<img width="1633" height="499" alt="image" src="https://github.com/user-attachments/assets/4df755ce-90dd-4db4-80f8-cebfdef03843" />
- Do là em chx gặp arbitrary read nên chx rõ phương pháp này lắm, nhưng mà nói chung là chỉ cần thỏa các requirement là có thể xài đc
### Arbitrary write
- Đối với phương pháp này thì em có thể dùng để leak data mà em muốn, chẳng hạn như địa chỉ libc hay heap address
<img width="1084" height="583" alt="image" src="https://github.com/user-attachments/assets/46ed2482-bc23-4d75-9050-c754a556a411" />
- Giống như arbitrary read, em cũng cần phải thỏa mãn các điều kiện trên để thực hiện phương pháp này
- Và đồng thời khi em thỏa mãn các điều kiện trên thì các ptr khác như thế nào cx đc
<img width="1819" height="700" alt="image" src="https://github.com/user-attachments/assets/ec28fdc5-1a97-4545-8e35-af7f9be61692" />
<img width="1752" height="549" alt="image" src="https://github.com/user-attachments/assets/13605cb0-d404-4347-9fff-8bfb5ed5e1b3" />
- Và như hình 1 thì cần phải chú ý read end = write_base
- Tiếp theo thì chỉ cần quan tâm mỗi write base với write ptr là đc
- khoảng cách giữa write ptr và base sẽ là vùng mà program in data ra trong lần thực thi 1 hàm in dữ liệu bất kì tiếp theo
<img width="451" height="224" alt="image" src="https://github.com/user-attachments/assets/9450d369-8149-402b-a37c-17f61de3a7e3" />
- Ảnh trên là 1 vd điển hình, nó sẽ in data trong vùng mik đã điều khiển trc r tới data trọng tâm là "Done!"
- Tuy nhiên, trong 1 số trường hợp thì vùng write_end có thể cũng có sức ảnh hưởng
- Tại vì khi em chạy trên chall ở task hiện tại thì chương trình có thể bị lỗi j đó khiến nó ko in dữ liệu ra như thường
-  Và sau khi em thay đổi write_end = write_ptr thì nó mới chịu in ra data như thường
- Mà file struct cũng có 1 thành phần khá quan trọng tên là vtable
### Vtable
- Kiến thức này thì em ko có sử dụng trong chall hiện tại nhưng em tìm hiểu thì thấy có vẻ cx cần thiết trong các chall khó
<img width="741" height="718" alt="image" src="https://github.com/user-attachments/assets/34f78c6f-62f7-4c97-aac0-1bb836395668" />
- Đó là ngoài file struct bth sẽ có 1 vùng gọi là vtable
- Và vùng này mik có thể tạo 1 vtable fake đc
<img width="1759" height="775" alt="image" src="https://github.com/user-attachments/assets/10373193-81eb-44f0-92c0-11376fffea52" />
- Lý do là vì tới 1 điểm nào đó thì sẽ có lệnh như hình dưới
<img width="1766" height="568" alt="image" src="https://github.com/user-attachments/assets/39868f16-7aec-48e1-a173-8996810b96e2" />
- Nếu như em đã tạo fake vtable và overwrite trước thì sẽ có cơ hội nhảy vô nơi em muốn
- Nhưng mà đáng tiếc là các bản libc mới thì nó sẽ có cơ chế check vtable có hợp lệ hay ko
- Do đó sẽ phải thực hiện thêm vài bước để thực sự nhảy vô đc fake vtable
- Nhưng mà kiến thức này khá sâu và xa nên em tạm bỏ qua, chừng nào gặp thì em sẽ đào thêm
- Tài liệu mà em tham khảo chủ yếu là pwn college, em sẽ lưu ở dây để tiện các lần sau nếu em cần xem lại wu
- https://docs.google.com/presentation/d/1Rs04LzYjD4eQ4_TJZCMDJMS8UNcpQ_OXcBpxzKpanC4/edit?slide=id.g205983036a9_0_28#slide=id.g205983036a9_0_28
- https://pwn.college/software-exploitation/file-struct-exploits
- Kĩ thuật nâng cao hơn về fsop:
+ https://blog.kylebot.net/2022/10/22/angry-FSROP/#PC2ROP
