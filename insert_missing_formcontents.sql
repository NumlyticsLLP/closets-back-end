--To be Updated (Last Changed 19-12-2025)
BEGIN
    DECLARE v_qty INT;
    DECLARE v_count INT DEFAULT 0;
    DECLARE v_max_suffix INT DEFAULT 0;
    DECLARE v_job_prefix VARCHAR(100);
    DECLARE v_new_jobid VARCHAR(100);
    DECLARE v_clientName VARCHAR(255);
    DECLARE v_projectname VARCHAR(255);
    DECLARE v_jsoncontent TEXT;
    DECLARE i INT DEFAULT 1;

    -- Extract values from JSON
    SET v_qty = CAST(JSON_UNQUOTE(JSON_EXTRACT(p_json, '$.closetsFormCount')) AS UNSIGNED);
    SET v_clientName = JSON_UNQUOTE(JSON_EXTRACT(p_json, '$.clientName'));
    SET v_projectname = 'New *';

    -- Get jobid prefix (e.g., "396895" from "396895-2")
    SET v_job_prefix = SUBSTRING_INDEX(p_jobid, '-', 1);

    -- Count current non-deleted records for this job
    SELECT COUNT(*) INTO v_count
    FROM formcontents
    WHERE jobid LIKE CONCAT(v_job_prefix, '-%') AND isdeleted = 0;

    -- Get max suffix used so far (even if deleted)
    SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(jobid, '-', -1) AS UNSIGNED)), 0)
    INTO v_max_suffix
    FROM formcontents
    WHERE jobid LIKE CONCAT(v_job_prefix, '-%');

    -- Insert only if more closets needed
    WHILE v_count + i <= v_qty DO
        SET v_new_jobid = CONCAT(v_job_prefix, '-', v_max_suffix + i);

        SET v_jsoncontent = JSON_OBJECT(
            'jobId', v_new_jobid,
            'clientName', v_clientName,
            'userId', CAST(p_userid AS CHAR),
            'projectname', v_projectname,
            'sameasabove', FALSE,
            'address', '',
            'city', '',
            'province', '',
            'postalCode', '',
            'cuttingarea', '',
            'collection', '',
            'collectionclr', '',
									
									 
            'tearout', '',									
            'additionalNotes', '',
            'condo', JSON_OBJECT(
                'hasCondos', NULL,
                'housenumber', ''
            ),
            'existingBoard', JSON_OBJECT(
                'notch', FALSE,
                'remove', FALSE
            ),
            'doors', JSON_OBJECT(
                'sameascollectioncolor', FALSE,
                'doorclosetcollection', '',
                'doorcolor', '',
									 
                'quantity', '',
                'decostyle', '',
                'series', '',
                'variant', '',
                'gripType', '',
                'gripSeries', '',
                'gripSize', '',
                'gripColor', ''
            ),
			'specialdoors', JSON_OBJECT(
                'specialDoorQuantity', '',
                'specialDoorType', '',
                'specialDoorSize', '',
                'specialDoorHeight', '',
                'specialDoorInsert', '',
                'specialDoorFrame', '',
                'specialDoorEdge', ''
            ),
            'drawers', JSON_OBJECT(
                'sameascollcolor', FALSE,
                'drawerclosetcollection', '',
                'drawercolor', '',
									   
                'quantity', '',
                'decostyle', '',
                'series', '',
                'variant', '',
                'gripType', '',
                'gripSeries', '',
                'gripSize', '',
                'gripColor', ''
            ),
            'rods', JSON_OBJECT(
									
                'quantity', '',
                'style', '',
                'color', ''
            ),
			'racks', JSON_ARRAY(),
            'baskets', JSON_ARRAY(),
            'hooks', JSON_ARRAY(),
            'hampers', JSON_ARRAY(),
            'counterTop', JSON_OBJECT(
										   
                'type', '',
                'color', '',
                'edge', ''
            ),
            'moulding', JSON_OBJECT(
								   
                'top', '',
									  
                'bottom', ''
            )
        );

        INSERT INTO formcontents (userid, jobid, jsoncontent, isdeleted)
        VALUES (p_userid, v_new_jobid, v_jsoncontent, 0);

        SET i = i + 1;
    END WHILE;
END;
