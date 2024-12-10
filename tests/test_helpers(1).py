import pytest
import json
from helpers import get_order_split
#Test helper.py
#author：bingrui li
@pytest.fixture
def prepared_order_constants(tmp_path):
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir() 
    file_path = logs_dir / "order_constants.json"
    
    file_path.write_text(json.dumps([
        {"type": "order_split", "value": 1}
    ])) 

    return file_path


def test_get_order_split(prepared_order_constants):
    file_content=str(prepared_order_constants)
    result = get_order_split(file_content)

    assert result == 1, "The order split value is incorrect."


# 测试文件是否存在
def test_file_not_found(prepared_order_constants):
    invalid_path = "xxxx/order_constants.json"

    with pytest.raises(FileNotFoundError):
        get_order_split(file_path=invalid_path)
