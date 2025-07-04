def analyze_body(metrics):
    shoulder = metrics["shoulder"]
    waist = metrics["waist"]
    hip = metrics["hip"]

    wsr = round(waist / shoulder, 2)
    whr = round(waist / hip, 2)

    if wsr < 0.75:
        shape = "V-Taper"
    elif whr < 0.8:
        shape = "Pear"
    elif whr > 1.0:
        shape = "Apple"
    else:
        shape = "Rectangle"

    if wsr < 0.75 and whr < 0.85:
        body_type = "Mesomorph"
    elif shoulder < hip:
        body_type = "Endomorph"
    else:
        body_type = "Ectomorph"

    return {
        "body_shape": shape,
        "body_type": body_type,
        "shoulder_to_waist_ratio": wsr,
        "waist_to_hip_ratio": whr
    }
