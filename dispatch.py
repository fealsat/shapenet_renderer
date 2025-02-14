import os
import json
import argparse
import subprocess


def collect_files(directory, extensions):
    """Collects all files with specified extensions in a given directory."""
    files = []
    for f in os.listdir(directory):
        if f in extensions:
            files.append(os.path.join(directory, f))
    return files


def distribute_files(files, num_jobs):
    job_lists = [[] for _ in range(num_jobs)]
    total_files = len(files)
    batch_size = total_files // num_jobs
    batch_rem = total_files % num_jobs
    # distribute the files to the number of jobs
    for job in range(num_jobs):
        job_lists[job].append(files[batch_size * job:batch_size * (job + 1)])
    # add remainder of files to last job
    job_lists[-1].append(files[batch_size * num_jobs:batch_size * num_jobs + batch_rem])
    return job_lists


def save_job_config(root_path, job_lists, output_json):
    """Saves the job distribution to a JSON file."""
    job_data = {"root_path": root_path, "files": job_lists}
    with open(output_json, 'w') as f:
        json.dump(job_data, f, indent=4)


def launch_blender_jobs(num_jobs, json_file, blender_script, config_file):
    """Launches Blender in headless mode with the specified script and job data."""
    for job_id in range(num_jobs):
        command = [
            "blender", "--background", "--python", blender_script, "--",
            "--batch_file", json_file, "--batch_id", job_id, "--config", config_file
        ]
        subprocess.Popen(command)
        print(f"Started job {job_id} with command: {' '.join(command)}")


def main():
    parser = argparse.ArgumentParser(description="Dispatch Blender jobs")
    parser.add_argument("--d", type=str, help="Directory containing 3D models")
    parser.add_argument("--script", type=str, help="Blender Python script to execute")
    parser.add_argument("--config", type=str, help="Config file to load")
    parser.add_argument("--num_jobs", type=int, default=4, help="Number of parallel jobs (default: 4)")
    parser.add_argument("--output_json", type=str, default="jobs.json", help="JSON file to store job allocation")

    args = parser.parse_args()

    extensions = ["gltf", "obj", "ply"]
    files = collect_files(args.directory, extensions)

    if not files:
        print("No valid 3D model files found. Exiting.")
        return

    job_lists = distribute_files(files, args.num_jobs)
    save_job_config(args.directory, job_lists, args.output_json)

    print(f"Job configuration saved to {args.output_json}")
    launch_blender_jobs(args.num_jobs, args.output_json, args.blender_script)


if __name__ == "__main__":
    main()
