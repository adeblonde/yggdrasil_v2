############
# Network storage
############

resource "aws_s3_bucket" "storage_unit" {

    ### bucket name casting '_' into '-' and crop at 64 characters length
    bucket = substr(replace(lower(format("%s_%s_storage_unit", var.module_prefix, var.storage_name)), "_", "-"), 0, 63)

    acl = "private"

    server_side_encryption_configuration = {
        rule {
            apply_server_side_encryption_by_default {
                sse_algorithm = "AES256"
            }
        }
    }

    tags = merge(
        var.module_tags,
        {
            "name" = format("%s_%s_storage_unit", var.module_prefix, var.storage_name)
        }
    )

}